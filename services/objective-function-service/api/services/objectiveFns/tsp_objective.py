import numpy as np


class TSPObjective:
    @classmethod
    def calc_objective(cls, adj_matrix, counts, objFun):
        # TODO: other objective functions via objFun parameter
        return cls.compute_expectation(counts, np.array(adj_matrix))

    @classmethod
    def compute_expectation(cls, counts, AdjMatrix):
    
        """
        Computes expectation value based on measurement results
        
        Args:
            counts: dict
                    key as bitstring, val as count
               
            AdjMatrix: Adjacency matrix as numpy array
            
        Returns:
            avg: float
                 expectation value
        """
        avg = 0
        sum_count = 0
        n = len(AdjMatrix)
        print(counts)
        for bitstring, count in counts.items():
            path = cls.path_from_string(bitstring, n)
            path_length = cls.compute_path_length(path+[path[0]], AdjMatrix)
            avg += path_length * count
            sum_count += count
            
        return avg/sum_count

    @classmethod
    def path_from_string(cls, string, amount_nodes):
        path = [-1]*amount_nodes
        for i in range(amount_nodes):
            node_string = string[i*amount_nodes:i*amount_nodes+amount_nodes]
            node_position = node_string.find('1')
            path[node_position] = i
        return path

    @classmethod
    def compute_path_length(cls, path, AdjMatrix):
        length = 0
        for i,j in zip(path[:-1], path[1:]):
            length += AdjMatrix[i,j]
        return length