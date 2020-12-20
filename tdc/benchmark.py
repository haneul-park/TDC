import pandas as pd
import numpy as np
import os, sys, json 
import warnings
warnings.filterwarnings("ignore")

from .utils import *
from .metadata import get_task2category, bm_metric_names, benchmark_names, bm_split_names
from .evaluator import Evaluator

class BenchmarkGroup:
	def __init__(self, name, path = './data'):
		'''
		-- PATH
			-- ADMET_Benchmark
				-- HIA_Hou
					-- train.csv
					-- valid.csv
					-- test.csv
				-- Caco2_Wang
					-- train.csv
					-- valid.csv
					-- test.csv
				....
		from tdc import BenchmarkGroup
		group = BenchmarkGroup(name = 'ADMET_Group', path = 'data/')
		predictions = {}

		for benchmark in group:
		   name = benchmark['name']
		   train, valid, test = benchmark['train'], benchmark['valid'], benchmark['test']
		   ## --- train your model --- ##
		   predictions[name] = y_pred

		group.evaluate(predictions)
		# {'caco2_wang': 0.234, 'hia_hou': 0.786}

		benchmark = group.get('Caco2_Wang')
		train, valid, test = benchmark['train'], benchmark['valid'], benchmark['test']
		## --- train your model --- ##
		group.evaluate(y_pred, benchmark = 'Caco2_Wang')
		# 0.234

		group.get_more_splits()
		'''
		
		self.name = bm_group_load(name, path)
		self.path = os.path.join(path, self.name)
		self.datasets = benchmark_names[self.name]
		self.dataset_names = []

		for task, datasets in self.datasets.items():
			for dataset in datasets:
				self.dataset_names.append(dataset)


	def __iter__(self):
		self.index = 0
		self.num_datasets = len(self.dataset_names)
		return self

	def __next__(self):
		if self.index < self.num_datasets:
			dataset = self.dataset_names[self.index]
			print_sys('--- ' + dataset + ' ---')
			data_path = os.path.join(self.path, dataset)
			train = pd.read_csv(os.path.join(data_path, 'train.csv'))
			valid = pd.read_csv(os.path.join(data_path, 'valid.csv'))
			test = pd.read_csv(os.path.join(data_path, 'test.csv'))
			self.index += 1
			return {'train': train, 'valid': valid, 'test': test, 'name': dataset}
		else:
			raise StopIteration
			
	def get_auxiliary_train_valid_split(self, seed, benchmark):
		dataset = fuzzy_search(benchmark, self.dataset_names)
		data_path = os.path.join(self.path, dataset)
		train = pd.read_csv(os.path.join(data_path, 'train.csv'))
		valid = pd.read_csv(os.path.join(data_path, 'valid.csv'))
		train_val = pd.concat([train, valid]).reset_index(drop = True)
		if bm_split_names[self.name][dataset] == 'scaffold':
			out = create_scaffold_split(train_val, seed, frac = [0.875, 0.125, 0], entity = 'Drug')
		else:
			raise NotImplementedError
		return out

	def get(self, benchmark):
		dataset = fuzzy_search(benchmark, self.dataset_names)
		data_path = os.path.join(self.path, dataset)
		train = pd.read_csv(os.path.join(data_path, 'train.csv'))
		valid = pd.read_csv(os.path.join(data_path, 'valid.csv'))
		test = pd.read_csv(os.path.join(data_path, 'test.csv'))
		return {'train': train, 'valid': valid, 'test': test, 'name': dataset}

	def evaluate(self, pred, true = None, benchmark = None):
		if true is None:
			# test set evaluation
			metric_dict = bm_metric_names[self.name]
			out = {}
			for data_name, pred_ in pred.items():
				data_name = fuzzy_search(data_name, self.dataset_names)
				data_path = os.path.join(self.path, data_name)
				test = pd.read_csv(os.path.join(data_path, 'test.csv'))
				y = test.Y.values
				evaluator = eval('Evaluator(name = \'' + metric_dict[data_name] + '\')')
				out[data_name] = {metric_dict[data_name]: round(evaluator(y, pred_), 3)}
			return out
		else:
			# validation set evaluation
			if benchmark is None:
				raise ValueError('Please specify the benchmark name for us to retrieve the standard metric!')
			data_name = fuzzy_search(benchmark, self.dataset_names)
			metric_dict = bm_metric_names[self.name]
			evaluator = eval('Evaluator(name = \'' + metric_dict[data_name] + '\')')
			return {metric_dict[data_name]: round(evaluator(true, pred), 3)}
