# code form https://github.com/snap-stanford/ogb/blob/master/examples/graphproppred/code2/gnn.py
import torch
from torch_geometric.nn import MessagePassing
from torch_geometric.nn import global_add_pool, global_mean_pool, global_max_pool, GlobalAttention, Set2Set
import torch.nn.functional as F
from torch_geometric.nn.inits import uniform

from src.model.conv import GNN_node, GNN_node_Virtualnode

from torch_scatter import scatter_mean

class GNN(torch.nn.Module):

    def __init__(self, num_vocab, max_seq_len, node_encoder, num_layer = 5, emb_dim = 300, 
                    gnn_type = 'gin', virtual_node = True, residual = False, drop_ratio = 0.5, JK = "last", graph_pooling = "mean", num_class=0, edge_attr_dim=2):
        '''
            num_tasks (int): number of labels to be predicted
            virtual_node (bool): whether to add virtual node or not
        '''

        super(GNN, self).__init__()

        self.num_class = num_class # if we do classification
        self.num_layer = num_layer
        self.drop_ratio = drop_ratio
        self.JK = JK
        self.emb_dim = emb_dim
        self.num_vocab = num_vocab
        self.max_seq_len = max_seq_len
        self.graph_pooling = graph_pooling

        if self.num_layer < 2:
            raise ValueError("Number of GNN layers must be greater than 1.")

        ### GNN to generate node embeddings
        if virtual_node:
            self.gnn_node = GNN_node_Virtualnode(num_layer, emb_dim, node_encoder, JK = JK, drop_ratio = drop_ratio, residual = residual, gnn_type = gnn_type, edge_attr_dim=edge_attr_dim)
        else:
            self.gnn_node = GNN_node(num_layer, emb_dim, node_encoder, JK = JK, drop_ratio = drop_ratio, residual = residual, gnn_type = gnn_type, edge_attr_dim=edge_attr_dim)


        ### Pooling function to generate whole-graph embeddings
        if self.graph_pooling == "sum":
            self.pool = global_add_pool
        elif self.graph_pooling == "mean":
            self.pool = global_mean_pool
        elif self.graph_pooling == "max":
            self.pool = global_max_pool
        elif self.graph_pooling == "attention":
            self.pool = GlobalAttention(gate_nn = torch.nn.Sequential(torch.nn.Linear(emb_dim, 2*emb_dim), torch.nn.BatchNorm1d(2*emb_dim), torch.nn.ReLU(), torch.nn.Linear(2*emb_dim, 1)))
        elif self.graph_pooling == "set2set":
            self.pool = Set2Set(emb_dim, processing_steps = 2)
        else:
            raise ValueError("Invalid graph pooling type.")

        self.graph_pred_linear_list = torch.nn.ModuleList()

        if self.num_class > 0:
            if graph_pooling == "set2set":
                self.graph_pred_linear = torch.nn.Linear(2*self.emb_dim, self.num_class)
            else:
                self.graph_pred_linear = torch.nn.Linear(self.emb_dim, self.num_class)
        else:
            if graph_pooling == "set2set":
                for i in range(max_seq_len):
                     self.graph_pred_linear_list.append(torch.nn.Linear(2*emb_dim, self.num_vocab))

            else:
                if self.num_vocab == 1:
                    self.graph_pred_linear_list.append(torch.nn.Sequential(
                        torch.nn.Linear(emb_dim, self.num_vocab), torch.nn.ReLU()))
                else:
                    for i in range(max_seq_len):
                         self.graph_pred_linear_list.append(torch.nn.Linear(emb_dim, self.num_vocab))


    def forward(self, batched_data):
        '''
            Return:
                A list of predictions.
                i-th element represents prediction at i-th position of the sequence.
        '''

        h_node = self.gnn_node(batched_data)

        h_graph = self.pool(h_node, batched_data.batch)

        if self.num_class > 0:
            return self.graph_pred_linear(h_graph)

        pred_list = []
        for i in range(self.max_seq_len):
            pred_list.append(self.graph_pred_linear_list[i](h_graph))

        return pred_list

if __name__ == '__main__':
    pass