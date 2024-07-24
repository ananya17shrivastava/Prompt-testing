# STEP 1-:

# QUERY FOR FINDING HICH DUPLICATED TO KEEP -:

# QUERY=SELECT s.id, s.name
# FROM solutions s
# INNER JOIN (
#     SELECT name, MIN(id) as min_id
#     FROM solutions
#     WHERE ai_generated = 1
#     GROUP BY name
#     HAVING COUNT(*) > 1
# ) as duplicates ON s.name = duplicates.name AND s.id = duplicates.min_id
# WHERE s.ai_generated = 1
# ORDER BY s.name;

import asyncio

from pathlib import Path
import json
import os

from db.mysql import fetch_duplicate_to_keep,fix_solutions


async def main():

    duplicates_to_keep=fetch_duplicate_to_keep()
    print(len(duplicates_to_keep))
    total_len=len(duplicates_to_keep)
    i=1
    # print(f"processing data {i} of {total_len}")

    for fixed_solution in duplicates_to_keep:
        print(f"processing data {i} of {total_len}")
        solution_id=fixed_solution['solution_id']
        solution_name=fixed_solution['solution_name']
        fix_solutions(solution_id,solution_name)
        i+=1








if __name__ == '__main__':
    asyncio.run(main())










