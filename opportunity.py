import asyncio

from pathlib import Path
import json
import os
from db.mysql import find_opportunities,insert_opportunity


async def main():

    opportunities=find_opportunities()
    i=0
    total_len=len(opportunities)
    print(total_len)
    # process.exit(0)
    for opportunity in opportunities:
        print(f"Inserting data {i+1} of {total_len}")

        usecase_id = opportunity['usecase_id']
        usecase_name = opportunity['usecase_name']
        industry_id = opportunity['industry_id']
        industry_category_id = opportunity['industry_category_id']
        business_area_id = opportunity['business_area_id']
        task_id = opportunity['task_id']
        solution_id = opportunity['solution_id']

        print("Inserting data !")
        insert_opportunity(
            usecase_id=usecase_id,
            usecase_name=usecase_name,
            industry_id=industry_id,
            industry_category_id=industry_category_id,
            business_area_id=business_area_id,
            task_id=task_id,
            solution_id=solution_id,
        )
        i+=1


if __name__ == "__main__":
    asyncio.run(main())




#     DELETE FROM opportunities
# WHERE created_at >= NOW() - INTERVAL 30 MINUTE;