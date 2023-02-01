# Linear Optimization on a Planning Problem
Solving a multi-objective planning problem using the Gurobi linear solver.

The data folder has example datasets with lists of workers and jobs. The objective is to find a planning to optimize multiple objectives:
- Maximize the total money generated (gain - penalties of jobs taken)
- Minimize the maximum amount of different jobs assigned to a worker
- Minimize the maximum duration of a project

Here is an example of different plannings according to different weights on the first two objectives (colors are different jobs assigned)

<p align="center">
  <img src="media\vizPlanning1.png" alt="Plannings" width="100%"/>
</p>

Maximizing money alone gets us the most amount of money (833) but it makes workers work on a lot of different jobs.

Maximizing money and minimizing the number of different jobs per worker reduces the money gain (290) because we take less jobs, but workers can focus on a single job during the month.