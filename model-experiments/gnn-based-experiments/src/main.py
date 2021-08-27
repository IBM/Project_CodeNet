# adapted https://github.com/snap-stanford/ogb/blob/master/examples/graphproppred/code2/main_pyg.py
import argparse
import random
import numpy as np
import torch.optim as optim
import pandas as pd
import torch.multiprocessing
from torchvision import transforms
from tqdm import tqdm
from ogb.graphproppred import Evaluator

from src.utils import augment_edge, ASTNodeEncoder
from src.model.gnn import GNN
from src.data.dataset import PygGraphPropPredDataset
from src.data.dataloader import DataLoader
from src.data.data_parallel import DataParallel
# make sure summary_report is imported after src.utils (also from dependencies)
from src.utils_file import *


torch.multiprocessing.set_sharing_strategy('file_system')
multicls_criterion = torch.nn.CrossEntropyLoss()

path = os.path.abspath(__file__)
path = path[:path.rindex("/")] + "/../"
PATH = os.path.abspath(path)


def train(model, device, loader, optimizer, args, evaluator):
    model.train()

    y_true = []
    y_pred = []
    loss_accum = 0
    for step, batch in enumerate(tqdm(loader, desc="Iteration")):
        # one b(atch) per device
        batch = [b for b in batch if not b.x.shape[0] == 1 and not b.batch[-1] == 0]
        if batch:
            pred = model(batch)
            optimizer.zero_grad()

            trg = torch.cat([b.y.to(device) for b in batch], dim=0)
            loss = multicls_criterion(pred, trg.to(torch.long).view(-1,))
            loss.backward()
            if args.clip > 0:
                torch.nn.utils.clip_grad_norm(model.parameters(), args.clip)
            optimizer.step()

            loss_accum += loss.item()

            y_true.append(trg.view(-1,1).detach().cpu())
            y_pred.append(torch.argmax(pred.detach(), dim=1).view(-1, 1).cpu())

    y_true = torch.cat(y_true, dim=0).numpy()
    y_pred = torch.cat(y_pred, dim=0).numpy()
    # print(y_true)
    # print(y_pred)
    input_dict = {"y_true": y_true, "y_pred": y_pred}
    return loss_accum / (step + 1), evaluator.eval(input_dict)


def eval(model, device, loader, evaluator):
    model.eval()

    y_true = []
    y_pred = []
    for step, batch in enumerate(tqdm(loader, desc="Iteration")):
        # one b(atch) per device
        batch = [b for b in batch if not b.x.shape[0] == 1]
        if batch:
            with torch.no_grad():
                pred = model(batch)

            y_true += [b.y.view(-1, 1).detach().cpu() for b in batch]
            y_pred.append(torch.argmax(pred.detach(), dim=1).view(-1, 1).cpu())

    y_pred = torch.cat(y_pred, dim=0)
    y_true = torch.cat(y_true, dim=0).view(y_pred.shape)
    y_true = y_true.numpy()
    y_pred = y_pred.numpy()
    # print(y_true)
    # print(y_pred)
    input_dict = {"y_true": y_true, "y_pred": y_pred}

    return evaluator.eval(input_dict)


def main():
    parser = argparse.ArgumentParser(description='GNN baselines on Project Codenet data with Pytorch Geometrics')
    parser.add_argument('--device', type=int, default=0,
                        help='which gpu to use if any (default: 0)')
    parser.add_argument('--gnn', type=str, default="gcn",
                        help='GNN gin, gin-virtual, or gcn, or gcn-virtual (default: gcn), ...')
    parser.add_argument('--drop_ratio', type=float, default=0,
                        help='dropout ratio (default: 0)')
    parser.add_argument('--num_layer', type=int, default=5,
                        help='number of GNN message passing layers (default: 5)')
    parser.add_argument('--emb_dim', type=int, default=300,
                        help='dimensionality of hidden units in GNNs (default: 300)')
    parser.add_argument('--feat_nums', type=str, default="",
                        help='comma separated string containing number of categories per feature '
                             '(default: "", meaning "let it be computed")')
    parser.add_argument('--batch_size', type=int, default=80,
                        help='input batch size for training (default: 128)')
    parser.add_argument('--epochs', type=int, default=1000,
                        help='number of epochs to train (default: 1000)')
    parser.add_argument('--num_workers', type=int, default=0,
                        help='number of workers (default: 0)')
    parser.add_argument('--dataset', type=str, default="small", choices={"small","Java250", "Python800", "C++1000", "C++1400"},
                        help='dataset name (default: python1k)')

    parser.add_argument('--filename', type=str, default="test",
                        help='filename to output result (default: test)')

    parser.add_argument('--dir_data', type=str, default=os.path.join(PATH, 'data'),
                        help='directory where data should be stored (default: REPOSITORY/data)')
    parser.add_argument('--dir_results', type=str, default=os.path.join(PATH, 'results'),
                        help='results directory (default: REPOSITORY/results)')
    parser.add_argument('--dir_save', default=os.path.join(PATH, 'saved_models'),
                        help='directory to save checkpoints in (default: REPOSITORY/saved_models)')
    parser.add_argument('--checkpointing', default=0, type=int, choices=[0, 1],
                        help='if you want to use checkpointing (1) or not (0) (default: 0)')
    parser.add_argument('--checkpoint', default="",
                        help='path of checkpoint if any')
    parser.add_argument('--runs', default=10, type=int,
                        help='number of runs (default: 10)')
    parser.add_argument('--clip', default=0, type=float,
                        help='clipping value if gradient clipping should be uses (default: 0) ')
    parser.add_argument('--lr', default=1e-3, type=float,
                        help='learning rate (default: 1e-3)')
    parser.add_argument('--patience', default=20, type=float,
                        help='patience (default: 20)')
    ###

    args = parser.parse_args()
    device = torch.device("cuda:" + str(args.device)) if torch.cuda.is_available() else torch.device("cpu")

    os.makedirs(args.dir_results, exist_ok=True)
    os.makedirs(args.dir_save, exist_ok=True)

    save_args(args, os.path.join(args.dir_results, "a_" + args.filename + '.csv'))

    train_file = os.path.join(args.dir_results, 'd_' + args.filename + '.csv')
    if not os.path.exists(train_file):
        with open(train_file, 'w') as f:
            f.write("run,e,loss,tr_acc,va_acc,te_acc\n")
    res_file = os.path.join(args.dir_results, args.filename + '.csv')
    if not os.path.exists(res_file):
        with open(res_file, 'w') as f:
            f.write("r,e,tr_acc,va_acc,te_acc\n")  # run, epoch, best results according to validation

    ### dataloading and splitting
    dataset = PygGraphPropPredDataset(name=args.dataset, root=os.path.abspath("../data") if args.dir_data is None else args.dir_data)
    print("Data loading done!")
    split_idx = dataset.get_idx_split()

    assert dataset[0].num_node_features <= args.emb_dim

    ### set the transform function
    # augment_edge: add next-token edge as well as inverse edges. add edge attributes.
    net = max(dataset.data.edge_type).item()+1 if hasattr(dataset.data, "edge_type") else 0
    dataset.transform = transforms.Compose([lambda data: augment_edge(data, net)])

    ### automatic acc evaluator. takes some dataset name as input
    evaluator = Evaluator("ogbg-ppa")

    edim = args.emb_dim
    dims = []
    dataset.data.x.abs_()  # ensure no negative -- should not be in there anyway
    if not args.feat_nums:  # need to find out
        for d in range(dataset.data.num_node_features):
            dims += [max(dataset.data.x[:, d]).item() + 1]
    else:
        dims = [int(s) for s in args.feat_nums.split(",")]

    ### Encode node features into emb_dim vectors.
    node_encoder = ASTNodeEncoder(edim, max_depth=20, enc_dims=dims)

    start_run = 1
    checkpoint_fn = ""
    train_results, valid_results, test_results = [], [], []     # on run level

    if args.checkpointing and args.checkpoint:
        s = args.checkpoint[:-3].split("_")
        start_run = int(s[-2])
        start_epoch = int(s[-1]) + 1

        checkpoint_fn = os.path.join(args.dir_save, args.checkpoint)  # need to remove it in any case

        if start_epoch > args.epochs:  # DISCARD checkpoint's model (ie not results), need a new model!
            args.checkpoint = ""
            start_run += 1

            results = load_checkpoint_results(checkpoint_fn)
            train_results, valid_results, test_results, train_curve, valid_curve, test_curve = results

    # start
    for run in range(start_run, args.runs + 1):
        # run-specific settings & data splits
        torch.manual_seed(run)
        random.seed(run)
        np.random.seed(run)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(run)
            torch.backends.cudnn.benchmark = True
            # torch.backends.cudnn.deterministic = True
            # torch.backends.cudnn.benchmark = False

        n_devices = torch.cuda.device_count() if torch.cuda.device_count() > 0 else 1
        train_loader = DataLoader(dataset[split_idx["train"]], batch_size=args.batch_size, shuffle=True,
                                  num_workers = args.num_workers, n_devices=n_devices)
        valid_loader = DataLoader(dataset[split_idx["valid"]], batch_size=args.batch_size, shuffle=False,
                                  num_workers=args.num_workers, n_devices=n_devices)
        test_loader = DataLoader(dataset[split_idx["test"]], batch_size=args.batch_size, shuffle=False,
                                 num_workers=args.num_workers, n_devices=n_devices)

        start_epoch = 1

        # model etc.
        model = init_model(args, node_encoder, numclass=dataset.num_classes, edge_attr_dim=net+2)

        print("Let's use", torch.cuda.device_count(), "GPUs! -- DataParallel running also on CPU only")
        device_ids = list(range(torch.cuda.device_count())) if torch.cuda.device_count() > 0 else None
        model = DataParallel(model, device_ids)
        model.to(device)

        optimizer = optim.Adam(model.parameters(), lr=args.lr)

        # overwrite some settings
        if args.checkpointing and args.checkpoint:
            # signal that it has been used
            args.checkpoint = ""

            results, start_epoch, model, optimizer = load_checkpoint(checkpoint_fn, model, optimizer)
            train_results, valid_results, test_results, train_curve, valid_curve, test_curve = results
            start_epoch += 1
        else:
            valid_curve, test_curve, train_curve = [], [], []

        # start new epoch
        for epoch in range(start_epoch, args.epochs + 1):
            old_checkpoint_fn = checkpoint_fn
            checkpoint_fn = '%s.pt' % os.path.join(args.dir_save, args.filename + "_" + str(run) + "_" + str(epoch))

            print("=====Run {}, Epoch {}".format(run, epoch))
            loss, train_perf = train(model, device, train_loader, optimizer, args, evaluator)
            valid_perf = eval(model, device, valid_loader, evaluator)
            test_perf = eval(model, device, test_loader, evaluator)

            print({'Train': train_perf, 'Validation': valid_perf, 'Test': test_perf})
            with open(train_file, 'a') as f:
                f.write("{},{},{:.4f},{:.4f},{:.4f},{:.4f}\n".format(run, epoch, loss, train_perf[dataset.eval_metric], valid_perf[dataset.eval_metric], test_perf[dataset.eval_metric]))

            train_curve.append(train_perf[dataset.eval_metric])
            valid_curve.append(valid_perf[dataset.eval_metric])
            test_curve.append(test_perf[dataset.eval_metric])

            if args.checkpointing:
                create_checkpoint(checkpoint_fn, epoch, model, optimizer, (train_results, valid_results, test_results, train_curve, valid_curve, test_curve))
                if run > 1 or epoch > 1:
                    remove_checkpoint(old_checkpoint_fn)

            best_val_epoch = np.argmax(np.array(valid_curve))
            if args.patience > 0 and best_val_epoch + 1 + args.patience < epoch:
                print("Early stopping!")
                break

        print('Finished training for run {} !'.format(run)+"*"*20)
        print('Best validation score: {}'.format(valid_curve[best_val_epoch]))
        print('Test score: {}'.format(test_curve[best_val_epoch]))

        with open(res_file, 'a') as f:
            results = [run, best_val_epoch, train_curve[best_val_epoch], valid_curve[best_val_epoch],test_curve[best_val_epoch]]
            f.writelines(",".join([str(v) for v in results]) + "\n")

        train_results += [train_curve[best_val_epoch]]
        valid_results += [valid_curve[best_val_epoch]]
        test_results += [test_curve[best_val_epoch]]

        results = list(summary_report(train_results)) + list(summary_report(valid_results)) + list(summary_report(test_results))
        # with open(res_file, 'a') as f:
        #     f.writelines(str(run)+ ",_," + ",".join([str(v) for v in results]) + "\n")
        print(",".join([str(v) for v in results]))

    results = list(summary_report(train_results)) + list(summary_report(valid_results)) + list(summary_report(test_results))
    with open(res_file, 'a') as f:
        f.writelines(str(run) + ",_," + ",".join([str(v) for v in results]) + "\n")
        # print(",".join([str(v) for v in results]))

    # we might want to add runs later
    # if args.checkpointing:
    #     remove_checkpoint(checkpoint_fn)


def init_model(args, node_encoder, numclass=275, edge_attr_dim=2):
    # this was only relevant for regression version
    n, m = 1, 1
    if args.gnn == 'gin':
        model = GNN(num_vocab=n, max_seq_len=m, node_encoder=node_encoder,
                    num_layer=args.num_layer, gnn_type='gin', emb_dim=args.emb_dim, drop_ratio=args.drop_ratio,
                    virtual_node=False, num_class=numclass, edge_attr_dim=edge_attr_dim)
    elif args.gnn == 'gin-virtual':
        model = GNN(num_vocab=n, max_seq_len=m, node_encoder=node_encoder,
                    num_layer=args.num_layer, gnn_type='gin', emb_dim=args.emb_dim, drop_ratio=args.drop_ratio,
                    virtual_node=True, num_class=numclass, edge_attr_dim=edge_attr_dim)
    elif args.gnn == 'gcn':
        model = GNN(num_vocab=n, max_seq_len=m, node_encoder=node_encoder,
                    num_layer=args.num_layer, gnn_type='gcn', emb_dim=args.emb_dim, drop_ratio=args.drop_ratio,
                    virtual_node=False, num_class=numclass, edge_attr_dim=edge_attr_dim)
    elif args.gnn == 'gcn-virtual':
        model = GNN(num_vocab=n, max_seq_len=m, node_encoder=node_encoder,
                    num_layer=args.num_layer, gnn_type='gcn', emb_dim=args.emb_dim, drop_ratio=args.drop_ratio,
                    virtual_node=True, num_class=numclass, edge_attr_dim=edge_attr_dim)
    else:
        raise ValueError('Invalid GNN type')

    return model


if __name__ == "__main__":
    main()
