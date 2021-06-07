# adapted https://github.com/snap-stanford/ogb/blob/master/examples/graphproppred/code2/utils.py
import torch


class ASTNodeEncoder(torch.nn.Module):
    '''
        Input:
            x: default node feature.
            depth: The depth of the node in the AST.

        Output:
            emb_dim-dimensional vector

    '''
    def __init__(self, emb_dim, max_depth, enc_dims=[]):
        super(ASTNodeEncoder, self).__init__()

        self.max_depth = max_depth
        if enc_dims:
            edim = emb_dim//(len(enc_dims) + 1)
            l = [torch.nn.Embedding(n, edim) for n in enc_dims]
            self.embs = torch.nn.ModuleList(l)
            rest = emb_dim - (edim * (len(enc_dims) + 1))
            self.depth_encoder = torch.nn.Embedding(self.max_depth + 1, edim+rest)
        else:
            self.embs = None
            self.depth_encoder = torch.nn.Embedding(self.max_depth + 1, emb_dim)


    def forward(self, x, depth):
        depth[depth > self.max_depth] = self.max_depth
        if self.embs is None:
            return torch.cat([x, self.depth_encoder(depth)], dim=-1)
        return torch.cat([enc(x[:, i]) for i, enc in enumerate(self.embs)]+[self.depth_encoder(depth)], dim=-1)


# VT: with ourgraphs the below "AST" edges etc do not have to be AST edges but may be arbitray (data flow etc)
def augment_edge(data, num_edge_type):
    '''
        Input:
            data: PyG data object
        Output:
            data (edges are augmented in the following ways):
                data.edge_index: Added next-token edge. The inverse edges were also added.
                data.edge_attr (torch.Long):
                    data.edge_attr[:,0]: whether it is a graph edge (0) for next-token edge (1)
                    data.edge_attr[:,1]: whether it is original direction (0) or inverse direction (1)
                    IF IN DATA: n types for graph edges
                    data.edge_attr[:, 1+n]: types, n > 0

    '''
    if num_edge_type > 0:  # hasattr(data, "edge_type"):
        # num_edge_type = max(data.edge_type).item()+1
        idx = data.edge_type  ##.view(-1, 1)
        edge_type = torch.zeros(idx.size()[0], num_edge_type).scatter_(1, idx, 1)
        # y_one_hot = y_one_hot.view(*y.shape, -1)
    else:
        # num_edge_type = 0
        edge_type = torch.zeros(data.edge_index.size()[1], 0)
    # print(num_edge_type)

    ##### AST edge
    edge_index_ast = data.edge_index
    edge_attr_ast = torch.zeros((edge_index_ast.size(1), 2))
    if num_edge_type:
        edge_attr_ast = torch.cat([edge_attr_ast, edge_type], dim=-1)

    ##### Inverse AST edge
    edge_index_ast_inverse = torch.stack([edge_index_ast[1], edge_index_ast[0]], dim = 0)
    edge_attr_ast_inverse = torch.cat([torch.zeros(edge_index_ast_inverse.size(1), 1), torch.ones(edge_index_ast_inverse.size(1), 1)], dim = 1)
    if num_edge_type:
        edge_attr_ast_inverse = torch.cat([edge_attr_ast_inverse, edge_type], dim=-1)

    ##### Next-token edge

    ## Obtain attributed nodes and get their indices in dfs order
    # attributed_node_idx = torch.where(data.node_is_attributed.view(-1,) == 1)[0]
    # attributed_node_idx_in_dfs_order = attributed_node_idx[torch.argsort(data.node_dfs_order[attributed_node_idx].view(-1,))]

    ## Since the nodes are already sorted in dfs ordering in our case, we can just do the following.
    attributed_node_idx_in_dfs_order = torch.where(data.node_is_attributed.view(-1,) == 1)[0]

    ## build next token edge
    # Given: attributed_node_idx_in_dfs_order
    #        [1, 3, 4, 5, 8, 9, 12]
    # Output:
    #    [[1, 3, 4, 5, 8, 9]
    #     [3, 4, 5, 8, 9, 12]
    edge_index_nextoken = torch.stack([attributed_node_idx_in_dfs_order[:-1], attributed_node_idx_in_dfs_order[1:]], dim = 0)
    edge_attr_nextoken = torch.cat([torch.ones(edge_index_nextoken.size(1), 1), torch.zeros(edge_index_nextoken.size(1), 1+num_edge_type)], dim = 1)


    ##### Inverse next-token edge
    edge_index_nextoken_inverse = torch.stack([edge_index_nextoken[1], edge_index_nextoken[0]], dim = 0)
    edge_attr_nextoken_inverse = torch.ones((edge_index_nextoken.size(1), 2))
    if num_edge_type:
        edge_attr_nextoken_inverse = torch.cat([edge_attr_nextoken_inverse, torch.zeros(edge_index_nextoken.size(1), num_edge_type)], dim = 1)


    data.edge_index = torch.cat([edge_index_ast, edge_index_ast_inverse, edge_index_nextoken, edge_index_nextoken_inverse], dim = 1)
    data.edge_attr = torch.cat([edge_attr_ast,   edge_attr_ast_inverse, edge_attr_nextoken,  edge_attr_nextoken_inverse], dim = 0)

    return data
