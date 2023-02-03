"""
Runs the Gurobi linear optimizer on the planning problem.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from gurobipy import Model, GRB, quicksum

# PREPROCESSING

# Open the json file
JSON_PATH = "data/medium_instance.json"
f = open(JSON_PATH, encoding="utf-8")
data = json.load(f)

# List the days, the qualifications, the workers and the jobs
list_days = range(1, data["horizon"] + 1)
list_quals = data["qualifications"]
list_workers = [x["name"] for x in data["staff"]]
list_jobs = [x["name"] for x in data["jobs"]]

# Create utility dictionaries
conge, qualifie, requirements, gain, penalite, itstoolate = {}, {}, {}, {}, {}, {}

# Fill the dictionaries
for personne in data["staff"]:
    worker = personne["name"]
    for qual in list_quals:
        # qualifie is a binary variable that is 1 if the worker has the qualification
        qualifie[worker, qual] = 1 * (qual in personne["qualifications"])
    for day in list_days:
        # conge is a binary variable that is 1 if the worker is on vacation
        conge[worker, day] = 1 * (day in personne["vacations"])
for projet in data["jobs"]:
    job = projet["name"]
    # gain is the reward of the job
    gain[job] = projet["gain"]
    for day in list_days:
        # itstoolate is a binary variable that is 1 if the job is late on the day
        itstoolate[job, day] = 1 * (day > projet["due_date"])
    # penalite is the daily penalty of the job
    penalite[job] = projet["daily_penalty"]
    for qual in list_quals:
        if qual in projet["working_days_per_qualification"]:
            # requirements is the number of days the job requires the qualification
            requirements[job, qual] = projet["working_days_per_qualification"][qual]
        else:
            requirements[job, qual] = 0

# Create the model
m = Model("Projet_SDP")
chosenjob = {}
planning = {}
estaffecte = {}
workedtoday={}
begin,end={},{}
# Create the variables
for job in list_jobs:
    chosenjob[job] = m.addVar(vtype=GRB.BINARY, name=f"chosenjob_{job}")
    begin[job] =  m.addVar(vtype=GRB.INTEGER, lb=0, name=f"begin_{job}")
    end[job] =  m.addVar(vtype=GRB.INTEGER, lb=0, name=f"end_{job}")
    for worker in list_workers:
        estaffecte[worker, job] = m.addVar(
            vtype=GRB.BINARY, name=f"estafecte_{worker}_{job}"
        )
        for qual in list_quals:
            for day in list_days:
                planning[worker, qual, day, job] = m.addVar(
                    vtype=GRB.BINARY, 
                    name=f"planning_{worker}_{qual}_{day}_{job}",
                )
    for day in list_days:
        workedtoday[job, day]=m.addVar(
            vtype=GRB.BINARY, name=f"workedtoday_{job}_{day}"
        )
nbmaxjobs = m.addVar(vtype=GRB.INTEGER, lb=0, name="nbmaxjobs")
maxlenjob = m.addVar(vtype=GRB.INTEGER, lb=0, name="maxlenjob")

# Create the constraints
for worker in list_workers:
    # Definition de nbmaxjobs
    m.addConstr(
        quicksum([estaffecte[worker,job] for job in list_jobs]) <= nbmaxjobs
    )
    for day in list_days:
        # Contrainte d'unicité d'affectation
        m.addConstr(
            quicksum(
                np.array(
                    [
                        [planning[worker, qual, day, job] for qual in list_quals]
                        for job in list_jobs
                    ]
                ).flatten()
            )
            <= 1
        )
        for qual in list_quals:
            for job in list_jobs:
                # Contrainte de qualification
                m.addConstr(planning[worker, qual, day, job] <= qualifie[worker, qual])
                # Contrainte de conge
                m.addConstr(planning[worker, qual, day, job] + conge[worker, day] <= 1)
                # definition de estaffecte(worker,job)
                m.addConstr(estaffecte[worker,job] >= planning[worker,qual,day,job])
                # definition de workedtoday(job,day)
                m.addConstr(planning[worker, qual, day, job] <= workedtoday[job, day])

M = 10**6

for job in list_jobs:
    m.addConstr(1+end[job]-begin[job]<=maxlenjob)
    for day in list_days:
        # definition de begin(job)
        m.addConstr(day-begin[job]>=M*(workedtoday[job,day]-1))
        # definition de end(job)
        m.addConstr(end[job]-day>=M*(workedtoday[job,day]-1))
    for qual in list_quals:
        # Contrainte de completion des projets
        m.addConstr(
            requirements[job, qual] - M * (1 - chosenjob[job])
            <= quicksum(
                np.array(
                    [
                        [planning[worker, qual, day, job] for worker in list_workers]
                        for day in list_days
                    ]
                ).flatten()
            )
        )


# Create objective function
argent = quicksum(
    [
        gain[job] * chosenjob[job]
        - quicksum([itstoolate[job, day] * workedtoday[job,day] * penalite[job] for day in list_days])
        for job in list_jobs
    ]
)

m.setObjective(argent, GRB.MAXIMIZE)
m.Params.LogToConsole = 0

# epsilon=len(list_jobs)
# while epsilon>=0:
#     m.addConstr(nbmaxjobs<=epsilon)
#     m.optimize()
#     epsilon=nbmaxjobs.x-1
#     print(f"Argent : {m.objVal}, Nb_max_jobs : {nbmaxjobs.x}")
#     # for worker in list_workers:
#     #     print(worker)
#     #     for day in list_days:
#     #         for job in list_jobs:
#     #             for qual in list_quals:
#     #                 if planning[worker, qual, day, job].x==1:
#     #                     print(f"   day={day}, job={job}, qual={qual}")

# epsilon=len(list_days)
# while epsilon>=0:
#     m.addConstr(maxlenjob<=epsilon)
#     m.optimize()
#     epsilon=maxlenjob.x-1
#     print(f"Argent : {m.objVal}, max_len_job : {maxlenjob.x}")

epsilon1=len(list_days)
while epsilon1>=0:
    epsilon2=len(list_jobs)
    m.addConstr(maxlenjob<=epsilon1)
    constr_eps2 = m.addConstr(nbmaxjobs<=epsilon2)
    while epsilon2>=0:
        m.optimize()
        print(f"Argent : {m.objVal}, maxlenjob : {maxlenjob.x}, nbmaxjobs : {nbmaxjobs.x}")
        epsilon2=nbmaxjobs.x-1
        m.remove(constr_eps2)
        constr_eps2=m.addConstr(nbmaxjobs<=epsilon2)
    epsilon1-=1
    m.remove(constr_eps2)
    m.update()
    
    
    