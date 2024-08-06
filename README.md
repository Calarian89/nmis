# NMIS Data Ingest

Repo used to house notebooks and files used in our data pipeline through Databricks to ingest NMIS data to the EDL.

## Deployment

On merge to main will deploy Databricks infrastructure to production using templates found in Terraform directory. Infrastructure mostly consists of scheduled jobs that point to notebooks in this repository. Repository is sent to Databricks where they are hosted on a team repo. 

## Contributing

This repo uses [Poetry](https://python-poetry.org/) to manage dependencies. Make sure you have poetry installed according to the installation documentation, then run `poetry install` in the root of this repository.

### Organization

This repo is organized into a package, but that is a little misleading, as the main logic all lives in notebooks that run independently on Databricks.  The package hierarchy is only there to aid in running locally and testing. Here is some insight into our current structure:

- notebooks
  - All files found in this directory are ipynb notebooks. The logic inside each is expected to contain:
    1. A class or at least function definition that houses the main logic of that notebook. This is usually the first cell, but can span multiple if neccessary.
    2. One to multiple invocations of that logic meant to only ever be run against a databricks cluster.  This logic should be minimal, just enough to pass in parameters for different functionality, and usually the pre-existing Databricks spark session and/or dbutils. 
  - The logic in these notebooks cannot import any other files in this repo. They must be self sufficient to run on databricks clusters.
- tests
  - .py files run as tests.
    - They should leverage the ipynb library to import the notebook logic described above using `ipynb.fs.defs.{package_path_of_notebook}`.
      - Example: `from ipynb.fs.defs.notebooks.fetch_nmis_json_data import ServerInfo, DataRetriever`
      - This will only import function and class definitions. It will not execute function calls or any scripting.
- notebooks/local
  - Versions of the main notebooks meant to be run locally for development.
    - Should pull in the logic declared in the main level notebooks using the same method described above in tests, then provide arguments that allow the logic to run against a local python kernel, instead of a Databricks cluster.
    - This logic should be minimal, and usually consists of providing relative paths for files, and/or alternative versions of resources normally found on databricks clusters, described in more detail below.
- notebooks/local/utils
  - Utility classes or functions that aid in running databricks notebooks locally with minimal fuss.
    - spark_local
      - Simple helper to create a local spark session
    - dbutils_local
      - Replacement class for the Databricks dbutils that is automatically available on thier clusters. Usually used for interacting with file sytems or secrets.
        - This version does not exactly mimic all things the real dbutils does, but it is meant to be a way to not have to declare logic multiple times, and be able to leverage dbutils in our main notebooks without having to worry about complicating local notebook setups.

### Kernel Selection

If using VSCode, if you are wanting to run locally you should select the poetry kernel, instead of the default python kernel, when executing notebooks.
  - It will be the one with a path that starts with `~/.cache/pypoetry.../` and contains this project's name.
  - You may need a restart to discover the kernel after you run your first poetry install.

### Tasks

We leverage the [invoke](https://www.pyinvoke.org/) library to define tasks in the `tasks.py` file that you can use with `poetry run invoke {task}`. 

Some helpful ones include:
- `poetry run invoke lint`
  - Run linting and auto format files. Can send in the `--dry` option to not auto format.
- `poetry run invoke test`
  - Run all tests
      - You may pass in a `-k` parameter to specify a file or method name pattern to match if you wish.  Example: `poetry run invoke test -k enhance_`.
- `poetry run invoke verify`
  - Do all the things you would want to do before you check in your code, including linting, testing, and clearing ipynb outputs and widgets. 

### Automated Pipeline and Tasks

This repo requests PRs to merge to main.

- Black linting is enforced, even in notebook files.
- Unit testing is also enforced. All tests must pass before merging into the `main` branch.

Leverage the tasks defined in the `Tasks` section to verify you will pass these before you check in.

# Data Flow Diagram
```mermaid
sequenceDiagram
  autonumber
  participant A as NMIS
  participant B as Databricks<br>(Internal)
  participant C as NMIS Device Events<br>RAW
  participant D as Databricks<br>(Cloud)
  participant E as 'edl_stage' Database
  participant F as NMIS Device Events<br>ENHANCED
  
  note over A,F: Fetch NMIS Json Data Job<br>(Calls multiple servers for both routers and switches data)
  loop Runs every hour
    B->>+A: Auth POST
    A-->>-B: Cookie Header
    B->>+A: Routers or Switches Info GET
    A-->>-B: JSON Data
    B->>C: Write raw JSON responses
  end

  note over A,F: Load NMIS Json Job
  loop Runs every 3 hours
    D-->C: Consume all JSON files<br>from multiple directories
    D->>D: Parse files to dataframe using defined JSON schema 
    D->>C: Write out data to<br>centralized parquet table
    D-->C: Mark consumed files as processed
  end

  note over A,F: Enhance NMIS Data Job
  loop Runs every 6 hours starting at 1:00 am central
    D-->F: Get last processed timestamp
    D-->C: Get all records from raw parquet<br>table since that timestamp
    D->>D: Enhance and explode data into multiple dataframes
    D->>E: Write out dataframes to multiple tables
    D->>E: Add TBLPROPERTIES to those<br>tables for the EDL Sync Process
    D-->E: Monitor until the EDL<br>Sync Process completes
  end

  note over A,F: EDL Sync Process
  loop Runs continuously
    E->>E: Finds table with edl_state of 'edl_ready'
    E->>F: Adds new staging data<br>to relevant EDL table
    E->>E: Changes edl_state of table to edl_success
    E->>E: Deletes successful staged tables
  end

  note over A,F: Data Integrity Check Job
  loop Runs every 12 hours starting at 9:00 am
    D-->F: Run multiple queries to check data quality
  end
```

# ERD 
```mermaid
erDiagram
  nmis_device_events{
    string event_id pk
    timestamp event_timestamp
    string node_id
    string device_name
    int uptime_seconds
    string serial_number
    string model
    int total_device_interfaces
    int SNMP_enabled_interface_amount
    int location_id fk
    string tier
    string division
    string node_down_state
    string SNMP_state
    string system_name
    string device_type
  }

  device_locations{
    int	location_id pk,uk
    string	location
    string	region
    string	country
    string	state
    string	city
    timestamp	timestamp
    }

  nmis_device_event_interfaces{
    string	event_id fk
    string	interface_id uk
    string	name
    string	status
    boolean	SNMP_enabled
    int	speed_in_mbs
  }

  nmis_device_event_statuses{
    string	event_id fk
    string	type
    string	element
    string	status
    float	value
    string	index
  }

  nmis_device_event_temperatures{
    string event_id fk
    string state
    string sensor
  }

  nmis_device_events ||--|| device_locations : contains
  nmis_device_events ||--|{ nmis_device_event_interfaces : contains
  nmis_device_events ||--|{ nmis_device_event_statuses : contains
  nmis_device_events ||--|{ nmis_device_event_temperatures : contains
  
```