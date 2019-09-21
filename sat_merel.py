import numpy as np 
import random
import copy

def read_dimac(file):
	f=open(file,"r")
	f1=f.readlines()
	#https://stackoverflow.com/questions/28890268/parse-dimacs-cnf-file-python
	cnf = list()
	cnf.append(list())
	maxvar = 0

	for line in f1:
		tokens = line.split()
		if len(tokens) != 0 and tokens[0] not in ("p", "c"):
			for tok in tokens:
				lit = int(tok)
				maxvar = max(maxvar, abs(lit))
				if lit == 0:
					cnf.append(list())
				else:
					cnf[-1].append(lit)
	assert len(cnf[-1]) == 0
	cnf.pop()
	return cnf, maxvar

def add_puzzle(file, cnf):
	f=open(file, "r")
	f1=f.readlines()
	for line in f1:
		tokens = line.split()
		if len(tokens) != 0 and tokens[0] not in ("p", "c"):
			for tok in tokens:
				lit = int(tok)
				if lit == 0:
					cnf.append(list())
				else:
					cnf[-1].append(lit)
	assert len(cnf[-1]) == 0
	cnf.pop()

def check_unit_clause(cnf,dict_values):
	for clause in cnf:
		if len(clause)==1:
			for i in clause:
				if i not in dict_values:
					dict_values[i]=1
					dict_values[-i]=0
				elif dict_values[i]==0:
					print(i)
					print("ERROR, wrong truth value")
			#cnf.remove(clause)
	return(cnf, dict_values)

def check_tautology(cnf):
	cnf2=copy.deepcopy(cnf)
	for clause in cnf2:
		for i in clause:
			for j in clause:
				if i==-j:
					cnf.remove(clause)
	return cnf

def remove_true_clauses(cnf,dict_values):
	cnf2=copy.deepcopy(cnf)
	for clause in cnf2:
		rem_clause=False
		for i in clause:
			if i in dict_values and dict_values[i]==1:
				rem_clause=True
				continue
		if rem_clause:
			cnf.remove(clause)	
	return cnf

def remove_false_elements(cnf,dict_values):
	cnf2=copy.deepcopy(cnf)
	for clause in cnf2:
		clause_index=cnf.index(clause)
		for i in clause:
			if i in dict_values and dict_values[i]==0:
				cnf[clause_index].remove(i)
	return cnf

def check_if_backtracking_needed(cnf):
	for clause in cnf:
		if len(clause)==0:
			print('BACKTRACK!')
			return True
		else:
			return False

def correct_value_counter(dict_values):
	count=0
	for key in dict_values.keys():
		if key > 0 and dict_values[key]==1:
			count+=1
	return count


def random_fill(cnf, dict_values,list_random_filled):
	clause=cnf[random.randint(0,len(cnf)-1)]
	element = clause[random.randint(0,len(clause)-1)]
	if element in dict_values:
		print("element already in dict")
	elif element not in dict_values:
		dict_values[element]=1
		dict_values[-element]=0
		list_random_filled.append(element)
	return(dict_values, list_random_filled)

'''def dpll(cnf, dict_values,list_random_filled):
	cnf_copy=copy.deepcopy(cnf)
	cnf_copy2=copy.deepcopy(cnf)
	dict_values, list_random_filled=random_fill(cnf, dict_values,list_random_filled)
	cnf_copy=remove_false_elements(cnf_copy,dict_values)
	cnf_copy=remove_true_clauses(cnf_copy, dict_values)
	if check_if_backtracking_needed:
		dict_values[list_random_filled[-1]]=0
		dict_values[-list_random_filled[-1]]=0
		cnf_copy2=remove_false_elements(cnf_copy2,dict_values)
		cnf_copy2=remove_true_clauses(cnf_copy2, dict_values)
'''
def simplefy(cnf, dict_values):
	count=0
	previous_count=None
	while count != previous_count:
		previous_count=count
		cnf=remove_false_elements(cnf,dict_values)
		cnf=remove_true_clauses(cnf, dict_values)
		cnf, dict_values=check_unit_clause(cnf, dict_values)
		count=len(cnf)
	return cnf, dict_values



if __name__== "__main__":
	dict_values=dict()
	list_random_filled=[]
	cnf, maxvar=read_dimac("sudoku-rules.txt")
	add_puzzle("sudoku-example.txt", cnf)
	cnf=check_tautology(cnf)
	print(len(cnf))
	cnf, dict_values=simplefy(cnf,dict_values)
	if check_if_backtracking_needed(cnf):
		print('UNSAT')
	while cnf!=[]:
		dict_values, list_random_filled=random_fill(cnf, dict_values,list_random_filled)
		cnf, dict_values=simplefy(cnf,dict_values)
		print(len(cnf))
		check_if_backtracking_needed(cnf)
	print(dict_values)
	for key in dict_values.keys():
		if key > 0 and dict_values[key]==1:
			print(key)