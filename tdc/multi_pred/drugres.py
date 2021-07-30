"""Summary
"""
import warnings
warnings.filterwarnings("ignore")
import sys

from ..utils import print_sys
from . import bi_pred_dataset, multi_pred_dataset
from ..metadata import dataset_names

class DrugRes(bi_pred_dataset.DataLoader):

    """Data loader class to load datasets in Drug Response Prediction Task. 
    More info: https://tdcommons.ai/multi_pred_tasks/drugres/ 

    Task Description: Regression. Given the gene expression of cell lines and the SMILES of drug, predict the drug sensitivity level.


    """
    
    def __init__(self, name, path='./data', label_name=None,
                 print_stats=False):
        """Create Drug Response Prediction dataloader object
        
        Args:
            name (str): the dataset name.
            path (str, optional): 
                The path to save the data file, defaults to './data'
            label_name (str, optional): 
                For multi-label dataset, specify the label name, defaults to None
            print_stats (bool, optional): 
                Whether to print basic statistics of the dataset, defaults to False
        """
        super().__init__(name, path, label_name, print_stats,
                         dataset_names=dataset_names["DrugRes"])
        self.entity1_name = 'Drug'
        self.entity2_name = 'Cell Line'
        self.two_types = True

        if print_stats:
            self.print_stats()

        print('Done!', flush=True, file=sys.stderr)
