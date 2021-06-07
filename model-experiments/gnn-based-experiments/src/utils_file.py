import os
import torch
import statistics


def save_args(args, fn):
    with open(fn, 'w') as f:
        for k, v in args.__dict__.items():
            f.write("{},{}\n".format(k, v))
    print("saved args:", args)


def summary_report(val_list):
    return sum(val_list)/len(val_list), statistics.stdev(val_list) if len(val_list) > 1 else 0


def create_checkpoint(checkpoint_fn, epoch, model, optimizer, results):
    checkpoint = {"epoch": epoch,
                  "model": model.state_dict(),
                  "optimizer": optimizer.state_dict(),
                  "results": results}
    torch.save(checkpoint, checkpoint_fn)


def remove_checkpoint(checkpoint_fn):
    os.remove(checkpoint_fn)


def load_checkpoint(checkpoint_fn, model, optimizer):
    checkpoint = torch.load(checkpoint_fn)
    model.load_state_dict(checkpoint['model'])
    optimizer.load_state_dict(checkpoint['optimizer'])

    return checkpoint['results'], checkpoint['epoch'], model, optimizer


def load_checkpoint_results(checkpoint_fn):
    checkpoint = torch.load(checkpoint_fn)
    return checkpoint['results']

