# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 05:59:54 2019

@author: Jolene
"""

from __future__ import division
from __future__ import print_function
from ortools.sat.python import cp_model

import pandas as pd


        
    
    

def main():
    # This program tries to find an optimal assignment of nurses to shifts
    # (3 shifts per day, for 7 days), subject to some constraints (see below).
    # Each nurse can request to be assigned to specific shifts.
    # The optimal assignment maximizes the number of fulfilled shift requests.
    
    data = pd.read_excel('data.xlsx')
    data.dtypes
    staff = data.drop(['day','shift'], axis=1)
    staff = list(staff)
    
    shifts = data.filter(['shift'], axis=1)
    shifts = shifts.drop_duplicates()
    
    days = data.filter(['day'], axis=1)
    days = days.drop_duplicates().reset_index(drop = True)
    
    #shift_requests = data['day'].tolist()
    
    staff_shift_all = []
    for h in range(0,len(staff)):
        name = staff[h]
        data_staff = data.filter(['day','shift',name], axis=1)
        staff_shift = []
        staff_shift_all.append(staff_shift)
        
        for d in range(0,len(days)):
            day = days.day[d]
            shift_data = data_staff[data_staff['day'] == day].reset_index(drop = True)
            shift_data1 = shift_data[name].tolist()
            staff_shift.append(shift_data1)
        
        
        num_nurses = len(staff)
        num_shifts = len(shifts)
        num_days = len(days)
        all_nurses = range(num_nurses)
        all_shifts = range(num_shifts)
        all_days = range(num_days)
    shift_requests = staff_shift_all
#    shift_requests = [[[0, 0, 1], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1],
#                       [0, 1, 0], [0, 0, 1]],
#                      [[0, 0, 0], [0, 0, 0], [0, 1, 0], [0, 1, 0], [1, 0, 0],
#                       [0, 0, 0], [0, 0, 1]],
#                      [[0, 1, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0],
#                       [0, 1, 0], [0, 0, 0]],
#                      [[0, 0, 1], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0],
#                       [1, 0, 0], [0, 0, 0]],
#                      [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 0, 0], [1, 0, 0],
#                       [0, 1, 0], [0, 0, 0]]]
    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
    shifts = {}
    for n in all_nurses:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d,
                        s)] = model.NewBoolVar('shift_n%id%is%i' % (n, d, s))

    # Each shift is assigned to exactly one nurse in .
    for d in all_days:
        for s in all_shifts:
            model.Add(sum(shifts[(n, d, s)] for n in all_nurses) == 1)

    # Each nurse works at most one shift per day.
    for n in all_nurses:
        for d in all_days:
            model.Add(sum(shifts[(n, d, s)] for s in all_shifts) <= 1)

    # min_shifts_assigned is the largest integer such that every nurse can be
    # assigned at least that number of shifts.
    min_shifts_per_nurse = (num_shifts * num_days) // num_nurses
    max_shifts_per_nurse = min_shifts_per_nurse + 1
    for n in all_nurses:
        num_shifts_worked = sum(
            shifts[(n, d, s)] for d in all_days for s in all_shifts)
        model.Add(min_shifts_per_nurse <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_nurse)

    model.Maximize(
        sum(shift_requests[n][d][s] * shifts[(n, d, s)] for n in all_nurses
            for d in all_days for s in all_shifts))
    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.Solve(model)
    for d in all_days:
        print('Day', d)
        for n in all_nurses:
            for s in all_shifts:
                if solver.Value(shifts[(n, d, s)]) == 1:
                    if shift_requests[n][d][s] == 1:
                        print('Employee', n + 1, 'works shift', s + 1, '(requested).')
                    else:
                        print('Employee', n + 1, 'works shift', s + 1, '(not requested).')
        print()

    # Statistics.
    print()
    print('Statistics')
    print('  - Number of shift requests met = %i' % solver.ObjectiveValue(),
          '(out of', num_nurses * min_shifts_per_nurse, ')')
    print('  - wall time       : %f s' % solver.WallTime())


if __name__ == '__main__':
    main()