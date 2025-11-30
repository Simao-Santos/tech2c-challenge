# tech2c-challenge

## How to run
Make sure you have `docker` and `docker-compose` installed.

### Docker Installation Guides
- **Windows:** https://docs.docker.com/desktop/install/windows-install/
- **macOS:** https://docs.docker.com/desktop/install/mac-install/
- **Linux:** https://docs.docker.com/engine/install/

### Docker Compose Installation Guides
> *Note: Docker Desktop (Windows/macOS) includes Docker Compose automatically.*
- **Linux:** https://docs.docker.com/compose/install/

Afterwards just run `docker-compose up --build -d` and access [http://localhost:3001/](http://localhost:3001/)

## Testing
In order to run the backend tests, after running the docker containers, run `docker-compose exec backend python3 manage.py test -v 2` and see the output on the console.
The tests are available in `backend/dashboard/tests.py`.

## Project Explanation - Data Extraction and Process
When running the web app in the above url, the user sees an "Import CSV" button.
This allows the user to select a valid csv file (the valid headers are hinted) and it's data is afterwards, processed to be saved to the database.

The .csv validation involves:
- the verification of the .csv file, if it is not empty and has headers.
- Checking if the headers match the ones defined in `backend/dashboard/csv_config.py`
- Checking if the rows' values are correct (if possible converts, for example, string to float; converts ',' to '.' so it's a valid decimal point).

The EmissionRecord model has a unique constraint of company name, year and sector, so it's uniquely identifiable.

When the data ingestion is occuring we also validate the data itself, as in, each row, and log any error to present to the user at the end of the operation.
These errors can be:
- missing required values for the required fields (for example, missing the company name).
- having duplicate entries (same name, year and sector). In these cases, since there is no timestamp to know which one is most recent, in order to deduplicate, I decided to choose as valid the one that has the highest emissions and energy consumption. Basically to choose the worst case scenario. It's better to have a false positive than a false negative.
- Any invalid data format.
- Any other unpredicted exception.

Now the actual database operations begin. For each row we create a new EmissionRecord and compare if there is already an existing record and update it if any difference between them exists. These metrics are all logged and presented to the user at the end.
In order to improve performance, all database operations are performed in bulk.

In the end, as mentioned above, the user can see the feedback of the operations in a modal that contains the following information:
```py                
{
    "message": "CSV import completed successfully",
    "created": created_count,
    "updated": updated_count,
    "errors": errors, # list
    "total_processed": created_count + updated_count
}
```
Finally all the charts are visible with the data that was just processed.

## Project Explanation - Tech Stack
### Database
For the Database I chose __PostgreSQL__ for 3 reasons:
1. the data originally is in a tabular form, so an SQL database is appropriate; 
2. PostgreSQL is used extensively for analytical data and where data integrity is priority;
3. PostgreSQL is the database I have most experience and am most comfortable with.

### Backend
For the backend I chose __Django Rest Framework__, since Django is one of the backend frameworks I'm most comfortable with, although looking back, I could have chosen any another one, since my experience is mostly when using Django as a web framework and not as REST API. Although the similarities with data modelling, the ORM and overall project setup definitely sped up the process.

### Frontend
Since from what I understood Tech2C uses __React__ as the frontend framework, and since for the backend I didn't use your backend technology of choice I figured we could meet halfway.
__React__ is also a very popular framework which means there are a lot of information on it online, which made it ideal for a simple dashboard. Additionally I used __TailwindCSS__ for CSS classes.

### Honorable Mentions
For the UI design I used for the first time __Lovable__.

API testing and debug I used __Postman__.

Containerization, __Docker__ of course so it's easier to orchestrate everything.