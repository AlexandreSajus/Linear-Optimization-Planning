# Linear Optimization on a Planning Problem
Solving a multi-objective planning problem using the Gurobi linear solver.

The data folder has example datasets with lists of workers and jobs. The objective is to find a planning to optimize multiple objectives:
- Maximize the total money generated (gain - penalties of jobs taken)
- Minimize the maximum amount of different jobs assigned to a worker
- Minimize the maximum duration of a project

Here is the Pareto Surface of the planning problem on the medium data instance, it reprensents non-dominated solutions to the problem i.e solutions that don't have alternatives that are clearly superior (better on every objective)

<p align="center">
  <img src="media\pareto2.png" alt="Pareto Surface" width="80%"/>
</p>

We can choose solutions according to this plot. For example, if we want to choose a planning where workers work maximum 2 projects and projects last maximum 15 days for focus purposes, we can gain 326 in monetary gain maximum using this planning:

<p align="center">
  <img src="media\planningmedium.png" alt="Example Solution" width="80%"/>
</p>

We can also choose solutions according to a weighted sum of objectives. For example, here are the plannings if we choose according to money gained and maximum number of projects per worker:

<p align="center">
  <img src="media\vizPlanning1.png" alt="Weighted Sum Objective" width="80%"/>
</p>

If we only consider money as an objective, we gain a lot of money but workers have to work on more than 5 different projects during the week which is not ideal. If we limit the number of projects per worker to 2, the colors representing the different jobs become more uniform per worker, but the money gained reduces from 833 to 517
