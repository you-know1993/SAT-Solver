#Need to add the pure literal thingy
import random
import time
import copy
import operator
import glob
import os
import csv

def read_dimac(file):
	f=open(file,"r")
	f1=f.readlines()
	#https://stackoverflow.com/questions/28890268/parse-dimacs-cnf-file-python
	cnf = list()
	cnf.append(list())
	maxvar = 0
	minvar = 0

	for line in f1:
		tokens = line.split()
		if len(tokens) != 0 and tokens[0] not in ("p", "c"):
			for tok in tokens:
				lit = int(tok)
				maxvar = max(maxvar, abs(lit))
				minvar = min(minvar, abs(lit))
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
	return len(f1)

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

def check_pure_lit(cnf, dict_values):
	positive=set()
	negative=set()
	for clause in cnf:
		for i in clause:
			if i < 0:
				negative.add(abs(i))
			elif i>0:
				positive.add(i)
	in_pos=positive.difference(negative)
	in_neg=negative.difference(positive)
	for i in in_pos:
		if i not in dict_values:
			dict_values[i]=1
			dict_values[-i]=0
	for i in in_neg:
		if i not in dict_values:
			dict_values[i]=0
			dict_values[-i]=1
	return cnf, dict_values


def check_tautology(cnf):
	cnf2=copy.deepcopy(cnf)
	for clause in cnf2:
		for i in clause:
			for j in clause:
				if i==-j:
					cnf.remove(clause)
	return cnf

def remove_true_clauses(cnf,dict_values):
	#cnf2=copy.deepcopy(cnf)
	for clause in [*cnf]:
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


def simplefy(cnf, dict_values): #THIS NEEDS IMPROVEMENT
	count=0
	previous_count=None
	while count != previous_count:
		previous_count=count
		cnf=remove_false_elements(cnf,dict_values)
		cnf=remove_true_clauses(cnf, dict_values)
		cnf, dict_values=check_unit_clause(cnf, dict_values)
		cnf, dict_values=check_pure_lit(cnf, dict_values)
		count=len(cnf)
	return cnf, dict_values

def random_selection(list_of_lists):
	clause=list_of_lists[random.randint(0,len(list_of_lists)-1)]
	element = clause[random.randint(0,len(clause)-1)]
	return element

def dynamic_largest_individual_sum(list_of_lists):
	dict_of_values=dict()
	for clause in list_of_lists:
		for element in clause:
			if element in dict_of_values:
				dict_of_values[element]+=1
			else:
				dict_of_values[element]=1
	return max(dict_of_values.items(), key=operator.itemgetter(1))[0]  #https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary

def two_sided_jeroslow_wang(list_of_lists):
	dict_of_values=dict()
	dict_of_polarised_values=dict()
	for clause in list_of_lists:
		for element in clause:
			if element in dict_of_values:
				dict_of_values[abs(element)]+=2**-abs(len(clause))
				dict_of_polarised_values[element]+=2**-abs(len(clause))
			else:
				dict_of_values[abs(element)]=2**-abs(len(clause))
				dict_of_polarised_values[element]=2**-abs(len(clause))
	positive=max(dict_of_values.items(), key=operator.itemgetter(1))[0]  #https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
	negative=-positive
	if negative not in dict_of_polarised_values:
		return positive
	elif positive not in dict_of_polarised_values:
		return negative
	elif dict_of_polarised_values[positive] >= dict_of_polarised_values[negative]:
		return positive
	else:
		return negative

def dp_algorithm_jw(list_of_lists, dict_of_answers, counter, switch_counter, up_counter):
	#https://gist.github.com/davefernig/e670bda722d558817f2ba0e90ebce66f
	if list_of_lists == []:
		return True, dict_of_answers, counter,switch_counter, up_counter
	elif [] in list_of_lists:
		return False, None, counter, switch_counter, up_counter

	#new_element=random_selection(list_of_lists) 
	new_element=two_sided_jeroslow_wang(list_of_lists)
	#new_element=dynamic_largest_individual_sum(list_of_lists) #should give a split_counter of 226 in the example?
	counter+=1
	#print(new_element)
	new_lol=copy.deepcopy(list_of_lists)
	new_doa=copy.deepcopy(dict_of_answers)
	new_doa[new_element]=1
	new_doa[-new_element]=0
	new_lol, new_doa=simplefy(new_lol,new_doa)

	satifible, new_dict, counter, switch_counter, up_counter=dp_algorithm_jw(new_lol, new_doa,counter,switch_counter, up_counter)
	if satifible:
		return satifible, new_dict, counter, switch_counter, up_counter

	new_lol=copy.deepcopy(list_of_lists)
	new_doa=copy.deepcopy(dict_of_answers)
	new_doa[new_element]=0
	new_doa[-new_element]=1
	new_lol, new_doa=simplefy(new_lol,new_doa)
	switch_counter+=1
	satifible, new_dict, counter, switch_counter, up_counter=dp_algorithm_jw(new_lol,new_doa, counter, switch_counter, up_counter)
	if satifible:
		return satifible, new_dict, counter, switch_counter, up_counter
	return False, None, counter, switch_counter, up_counter+1

def dp_algorithm_ran(list_of_lists, dict_of_answers, counter, switch_counter, up_counter):
	#https://gist.github.com/davefernig/e670bda722d558817f2ba0e90ebce66f
	if list_of_lists == []:
		return True, dict_of_answers, counter, switch_counter,  up_counter
	elif [] in list_of_lists:
		return False, None, counter,switch_counter,  up_counter

	new_element=random_selection(list_of_lists) 
	#new_element=two_sided_jeroslow_wang(list_of_lists)
	#new_element=dynamic_largest_individual_sum(list_of_lists) #should give a split_counter of 226 in the example?
	counter+=1
	#print(new_element)
	new_lol=copy.deepcopy(list_of_lists)
	new_doa=copy.deepcopy(dict_of_answers)
	new_doa[new_element]=1
	new_doa[-new_element]=0
	new_lol, new_doa=simplefy(new_lol,new_doa)

	satifible, new_dict, counter, switch_counter, up_counter=dp_algorithm_ran(new_lol, new_doa,counter, switch_counter, up_counter)
	if satifible:
		return satifible, new_dict, counter, switch_counter,  up_counter

	new_lol=copy.deepcopy(list_of_lists)
	new_doa=copy.deepcopy(dict_of_answers)
	new_doa[new_element]=0
	new_doa[-new_element]=1
	new_lol, new_doa=simplefy(new_lol,new_doa)
	switch_counter+=1
	
	satifible, new_dict, counter, switch_counter, up_counter=dp_algorithm_ran(new_lol,new_doa, counter,switch_counter, up_counter)
	if satifible:
		return satifible, new_dict, counter, switch_counter,up_counter
	return False, None, counter, switch_counter,up_counter+1

def dp_algorithm_dlis(list_of_lists, dict_of_answers, counter,switch_counter, up_counter):
	#https://gist.github.com/davefernig/e670bda722d558817f2ba0e90ebce66f
	if list_of_lists == []:
		return True, dict_of_answers, counter, switch_counter,up_counter
	elif [] in list_of_lists:
		return False, None, counter, switch_counter,up_counter
	print(counter)

	#new_element=random_selection(list_of_lists) 
	#new_element=two_sided_jeroslow_wang(list_of_lists)
	new_element=dynamic_largest_individual_sum(list_of_lists) #should give a split_counter of 226 in the example?
	counter+=1
	#print(new_element)
	new_lol=copy.deepcopy(list_of_lists)
	new_doa=copy.deepcopy(dict_of_answers)
	new_doa[new_element]=1
	new_doa[-new_element]=0
	new_lol, new_doa=simplefy(new_lol,new_doa)

	satifible, new_dict, counter, switch_counter,up_counter=dp_algorithm_dlis(new_lol, new_doa,counter, switch_counter, up_counter)
	if satifible:
		return satifible, new_dict, counter, switch_counter,up_counter

	new_lol=copy.deepcopy(list_of_lists)
	new_doa=copy.deepcopy(dict_of_answers)
	new_doa[new_element]=0
	new_doa[-new_element]=1
	new_lol, new_doa=simplefy(new_lol,new_doa)
	switch_counter+=1
	
	satifible, new_dict, counter, switch_counter,up_counter=dp_algorithm_dlis(new_lol,new_doa, counter, switch_counter,up_counter)
	if satifible:
		return satifible, new_dict, counter, switch_counter,up_counter
	return False, None, counter, switch_counter, up_counter+1

def do_jw(pathname):
	start=time.time()
	up=0
	new_val_counter=0
	switch=0
	answer=[]
	dict_values=dict()
	list_random_filled=[]
	cnf, maxvar=read_dimac("sudoku-rules.txt")
	num_given=add_puzzle(pathname, cnf)
	base=os.path.basename(pathname)
	puzzle=base.strip('.txt')
	cnf=check_tautology(cnf)
	cnf, dict_values=simplefy(cnf,dict_values)
	if [] in cnf:
		satifible=false
	else:
		satifible, dict_values, new_val_counter, switch, up=dp_algorithm_jw(cnf,dict_values, new_val_counter, switch,up)
	if satifible:
		#print ('SAT')
		for key in dict_values.keys():
			if key > 0 and dict_values[key]==1:
				answer.append(key)
		answer.sort()
		#print(answer)
		#print (counter)
		#print(up)
		return puzzle, num_given, 'SAT', 'Two-Sided Jeroslow-Wang', new_val_counter, switch, up, time.time()-start
	else:
		#print ('UNSAT')
		return puzzle, num_given, 'UNSAT','Two-Sided Jeroslow-Wang', None, None, None, time.time()-start

def do_dlis(pathname):
	start=time.time()
	up=0
	new_val_counter=0
	switch=0
	answer=[]
	dict_values=dict()
	list_random_filled=[]
	cnf, maxvar=read_dimac("sudoku-rules.txt")
	num_given=add_puzzle(pathname, cnf)
	base=os.path.basename(pathname)
	puzzle=base.strip('.txt')
	cnf=check_tautology(cnf)
	cnf, dict_values=simplefy(cnf,dict_values)
	if [] in cnf:
		satifible=false
	else:
		satifible, dict_values, new_val_counter, switch, up=dp_algorithm_dlis(cnf,dict_values, new_val_counter,switch,up)
	if satifible:
		#print ('SAT')
		for key in dict_values.keys():
			if key > 0 and dict_values[key]==1:
				answer.append(key)
		answer.sort()
		#print(answer)
		#print (counter)
		#print(up)
		return puzzle, num_given, 'SAT', 'Dynamic largest individual sum', new_val_counter, switch,up, time.time()-start
	else:
		#print ('UNSAT')
		return puzzle, num_given, 'UNSAT','Dynamic largest individual sum', None, None, None, time.time()-start

def do_ran(pathname):
	start=time.time()
	up=0
	new_val_counter=0
	switch=0
	answer=[]
	dict_values=dict()
	list_random_filled=[]
	cnf, maxvar=read_dimac("sudoku-rules.txt")
	num_given=add_puzzle(pathname, cnf)
	base=os.path.basename(pathname)
	puzzle=base.strip('.txt')
	cnf=check_tautology(cnf)
	cnf, dict_values=simplefy(cnf,dict_values)
	if [] in cnf:
		satifible=false
	else:
		satifible, dict_values, new_val_counter, switch, up=dp_algorithm_ran(cnf,dict_values, new_val_counter, switch, up)
	if satifible:
		#print ('SAT')
		for key in dict_values.keys():
			if key > 0 and dict_values[key]==1:
				answer.append(key)
		answer.sort()
		#print(answer)
		#print (counter)
		#print(up)
		return puzzle, num_given, 'SAT', 'Random', new_val_counter, switch, up, time.time()-start
	else:
		#print ('UNSAT')
		return puzzle, num_given, 'UNSAT','Random', None, None, None, time.time()-start

if __name__== "__main__":
	print(do_dlis('sudoku-example.txt'))
	for filename in glob.glob(f"sudokus/*.txt"):
		base=os.path.basename(filename)
		puzzle=base.strip('.txt')
		lines=[do_ran(filename), do_jw(filename), do_dlis(filename)]
		print(lines)
		with open('output-new.csv', 'a') as writeFile:
			writer = csv.writer(writeFile)
			writer.writerows(lines)

		