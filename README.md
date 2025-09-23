# Quisby
## 1. Overview
A Python-based tool to preprocess, visualize, and compare benchmark regression data directly in Google Spreadsheets.
### Purpose:
Quisby simplifies the complex task of analyzing benchmark results across multiple systems, OS versions, or hardware configurations. It allows developers, performance engineers, and data scientists to quickly transform raw benchmark outputs into actionable insights without manual spreadsheet work.
### Workflow Diagram:
```
Raw Benchmark Data
        |
        v
Quisby Data Extraction
        |
        v
Data Summarization & Cleaning
        |
        v
Google Sheets Upload & Visualization
        |
        v
Graphs, Comparisons & Reports
```
## 2. Target Audience
**Intended Users:**
* Developers and performance engineers analyzing system benchmarks.
* Data scientists and researchers comparing hardware/software performance.
* System administrators managing benchmark results across multiple machines or environments.


**Skill Level Required:**
* Basic familiarity with Python (for configuration and execution).
* Understanding of benchmark concepts (e.g., CPU, memory, storage performance).
* No advanced programming skills required; Quisby handles most preprocessing and visualization automatically.
## 3. Main Features / Capabilities
**Primary Functionalities:**
* Data Preprocessing: Automatically extracts, cleans, and summarizes benchmark data from multiple sources.
* Visualization: Generates charts and graphs in Google Sheets for quick interpretation of benchmark results.
* Spreadsheet Comparison: Compares multiple benchmark spreadsheets to identify trends, regressions, or improvements.
* Automation: Handles repetitive benchmark processing tasks, reducing manual effort.


**Supported Benchmarks:**
linpack, streams, specjbb, speccpu, fio, uperf, coremark, coremark_pro, passmark, pyperf, phoronix, etcd, auto_hpl, hammerdb, aim, pig, reboot.


**Supported Inputs / Formats:**
Benchmark output in .csv format files from supported tests.
Configuration files (config.ini) for specifying paths, spreadsheet names, and other settings.
Google Sheets for comparison and data visualization 


**Optional Features:**
* Logging for troubleshooting and audit trail (quisby.log).
* Centralized spreadsheet registry (charts.json) for quick access to results.


## 4. Prerequisites
**Software Dependencies:**
* *Python 3.9+ (recommended: 3.9.23)*
* *Python packages listed in requirements.txt* (e.g., boto3, google-api-python-client, numpy, scipy)
* *Accounts, Credentials, and API Usage*
Quisby requires Google OAuth credentials to access    Google Sheets and Drive. Follow these steps to create it:

Step 1: Enable Google Sheets & Drive API
  * Go to the Google Cloud Console.
   * Create a new project or select your existing project.
   * Navigate to APIs & Services → Library.
   * Enable the following APIs:
      * Google Sheets API
      * Google Drive API 

Step 2: Create OAuth Client ID
* Navigate to APIs & Services → Credentials → Create Credentials → OAuth client ID
* Select Desktop App as the application type.
* Download the JSON file.
* Rename the file to oauth_credentials.json.
* Move the file to the Quisby configuration folder:
* /home/<user>/.quisby/config/

    
Example folder structure:
```
/home/user/.quisby/config/
├── charts.json
├── config.ini
├── oauth_credentials.json
└── token.json
```

    
  Example oauth_credentials.json content:
```
{
  "installed": {
    "client_id": "95894xxxxxxxx.apps.googleusercontent.com",
    "project_id": "user-465515",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCXXXXXSyfr",
    "redirect_uris": ["http://localhost"]
  }
}
```

Note: Once you authenticate using these credentials, a token.json file will be automatically created for session management once at the beginning.
    
## 5. Installation 

* Clone the Repository:
```
git clone https://github.com/redhat-performance/quisby.git
cd quisby
```
* Create a Virtual Environment & Install Python:
```
pyenv install 3.9.23
pyenv virtualenv 3.9.23 quisby-env
pyenv activate quisby-env
```
* Upgrade pip, setuptools, wheel & Install Dependencies:
```
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

* Explore CLI Options:
```
python quisby.py --help
```

## 6. Configuration

1. config.ini – Main configuration file. Can be a custom path or default is set at ~/.quisby/config/config.ini

Sample
```
(myenv1) $ cat /home/user/.quisby/config/config.ini 
[test]
test_name = streams
test_path = /home/user/quisby/quisby/benchmarks
results_location = /home/user/quisby/m6g95results_location.txt
system_name = cloud
os_type = rhel
os_release = 9.5

[spreadsheet]
spreadsheet_name = aws-rhel-9.5-regression-test
spreadsheet_id = 14CtYe8GpgbpFKPhXsn59OQP3Msbd4i-qo3fnPPna-VI
comp_name = rhel9.5m7g and rhel9.6m7g
comp_id = 1zOcEZE0GhnxUVi9R3__KDAMvwTiSXOML9LF6x3Km_W8

[cloud]
region = us-east-1
cloud_type = aws

[dependencies]
specjbb_java_version = java-11-openjdk

[access]
users = user@redhat.com

[LOGGING]
level = INFO
filename = quisby.log
max_bytes_log_file = 5backup_count = 3
```

2. Results_location file - contains the short location of where all results.csv files coming from zathras/wrappers are saved. These files are expected to be under ~/quisby/quisby/benchmarks.

Example
```
$ ls -l ~/quisby/quisby/benchmarks
total 0
drwxr-xr-x. 1 user user 220 Sep 19 12:50 9.5csvfiles
drwxr-xr-x. 1 user user 184 Sep 17 09:40 9.6csvfiles
```
```
$ cat /home/user/quisby/results_location.txt
test phoronix
9.5csvfiles/95m6g_phoronix_results.csv,m6g.2xlarge
test streams
9.5csvfiles/95m6g_streams_results.csv,m6g.2xlarge
```
## 7. Usage Instructions
* List all Supported Benchmarks that Quisby can process 
```
$ python3 quisby.py --list-benchmarks
2025-09-23 11:54:01 [INFO] Supported benchmarks :
aim
auto_hpl
boot
coremark
coremark_pro
etcd
fio_run
hammerdb_maria
hammerdb_mssql
hammerdb_pg
linpack
passmark
phoronix
pig
pyperf
specjbb
speccpu
streams
uperf
```

* Run processing on benchmark results stored in default location
```
python3 quisby.py --process 
```

* Specify a custom configuration file:
```
python3 quisby.py --config /home/user/config.ini  --process
```

* Compare benchmark runs captured in 2 googlesheet IDs:
    
```
python3 quisby.py --compare 1yopZltconjg_549k8LfOig1g8J6buZny1Ry8-0wP3O4,1PKLHlJhcz6VsBzp8jnM0TsTjdkAOHOnpfq2kAJvszcM
```

* Compare specific benchmark from previous runs by spreadsheet IDs:
    
```
python3 quisby.py --compare 1yopZltconjg_549k8LfOig1g8J6buZny1Ry8-0wP3O4,1PKLHlJhcz6VsBzp8jnM0TsTjdkAOHOnpfq2kAJvszcM --compare-list streams,phoronix
```

    
## 8. Post-Execution
    
### **8.1 Storage Location**
After running Quisby, the benchmark results are generated and stored in spreadsheets either pre-existing or newly created.


### **8.2 Output Contents**
Your Quisby spreadsheet is organized into the following sheets for easy analysis:

1.  **Summary Sheet**
    * **Purpose:** A high-level overview for stakeholders. This sheet is a template for you to fill in.
    * **Key Contents:** Summaries of performance changes (gains, regressions), links to relevant Jira tickets, and the overall conclusion of the test run.

2.  **Detailed Benchmark Sheets**
    * **Purpose:** Contains the raw, detailed results for each benchmark.
    * **Key Contents:** Per-iteration scores, system information (CPU, memory, OS), and charts visualizing the raw performance.

3.  **Comparison Sheet (Generated with `--compare`)**
    * **Purpose:** Directly compares two test runs, such as different RHEL versions.
    * **Key Contents:** Side-by-side scores, absolute and percentage differences, and charts that are crucial for interpreting results.



### **8.3 Interpreting Outputs**

Interpreting Quisby's comparison charts is key to understanding true performance changes. The analysis depends on the type of benchmark and accounting for normal performance variations.


#### **Reading a Comparison Chart**

The fastest way to analyze a chart is to focus on three elements:

1. The Bars (Absolute Score)

These show the raw performance score. How you interpret them depends on the benchmark's goal:

* Throughput Benchmarks (Higher is better): For tests like SPEC CPU, HammerDB (TPM), or FIO (IOPS/Bandwidth), a taller bar is better.
* Latency Benchmarks (Lower is better): For tests like boot time or uperf latency, a shorter bar is better.

2. The Yellow Line (% Difference)

This line is your main indicator of change. Its meaning also depends on the benchmark type:

* For Throughput (Higher is better):
  * Positive %: Performance gain 
  * Negative %: Performance regression

* For Latency (Lower is better):
  * Positive %: Performance regression 
  * Negative %: Performance gain 

3. Accounting for Performance Noise

* Not every percentage change is significant. Small fluctuations are expected and are considered "noise."
* Before analyzing, define a noise threshold (e.g., ±5%).
* Only treat changes that exceed your threshold as meaningful gains or regressions. A change of +1% or -0.8% is likely just noise and should be considered "no significant change."

#### **Example 1: Clear Performance Improvement**
<img width="1916" height="1055" alt="Screenshot From 2025-09-23 14-22-37" src="https://github.com/user-attachments/assets/051c84d4-3468-4422-a6d5-3ebdaf995fc7" />

In this `speccpu2017` benchmark on large systems, the new RHEL version shows a clear performance gain. Notice how the **red bars (`rhel_96`) are consistently taller** and the **yellow line stays above 0%**, indicating a ~2% improvement across the board.

#### **Example 2: Mixed or Workload-Dependent Results**
<img width="1916" height="1055" alt="Screenshot From 2025-09-23 14-26-01" src="https://github.com/user-attachments/assets/c2d276c9-f606-4d2b-821d-bc3f48327d42" />

Performance changes aren't always positive for every workload. In this `hammerdb` database test, the results are **mixed**. The **yellow line goes both above and below zero**, showing that the OS upgrade improved performance on some systems (`m6a.24xlarge`) but caused a regression on others (`m6i.24xlarge`). This tells you the impact is dependent on the specific hardware or workload.

## 9. Error Handling / Troubleshooting
The first thing Quisby prints is the location of the log file. When Quisby runs into a problem,Check this file for detailed error messages that may not appear in the console. Understanding these common errors can help you fix issues quickly.


[ LOG LOCATION : /home/user/.quisby/logs/quisby.log ]

### **9.1 Common Errors and Fixes**
    

| Error / Warning | Possible Cause | Resolution / Notes |
| :--- | :--- | :--- |
| No configuration path mentioned | Quisby was run without the `--config` option or the default config file is missing. | Provide the config path explicitly: <br> `python3 quisby.py --process --config ~/.quisby/config/config.ini` |
| OAuth credentials not found at /home/sbhavsar/.quisby/config/ | The required `oauth_credentials.json` file is missing from the `~/.quisby/config/` directory. | Ensure you've downloaded the oauth credentials key from your Google Cloud project and placed it in the correct location. |
| Mentioned benchmark not yet supported ! | The benchmark name in `config.ini` is not currently supported by Quisby. | Check the benchmark spelling in `config.ini`. Refer to `python3 quisby.py --list-benchmarks` for supported benchmarks. |
| Unable to extract data from csv file for <benchmark> | The CSV file path is missing, empty, or incorrectly formatted. | Verify the `results_location.txt` file points to the correct benchmark result CSV files. Ensure CSVs are not corrupted. |
    
    
Here are some frequently asked questions and tips to help you get the most out of Quisby.


## 11. FAQ / Tips

#### **1. How can I quickly compare results without reprocessing all the data?**

You don't need to rerun the `--process` command every time. Once your data is in Google Sheets, you can use the `--compare` flag with the Spreadsheet IDs to generate a new comparison sheet instantly. This is the recommended practice for quick analysis.

```bash
# Compare two existing spreadsheets
python3 quisby.py --compare SPREADSHEET_ID_1,SPREADSHEET_ID_2
```


#### **2. My comparison chart looks cluttered. How can I fix it?**

If a comparison sheet has too many benchmarks, the charts can become hard to read. Use the `--compare-list` flag to generate a comparison for only the specific benchmarks you're interested in.

```bash
# Only compare streams and phoronix results from the two sheets
python3 quisby.py --compare ID_1,ID_2 --compare-list streams,phoronix
```



#### **3. Can I process results for a new, unsupported benchmark?**

Not directly. Quisby relies on specific parsers for each benchmark it supports. Adding a new benchmark requires writing a new parser in the Python code. If you need a new benchmark supported, please file an issue on the official Quisby GitHub repository.



#### **4. What's the easiest way to share my results with my team?**

The best way is to add your team members' email addresses to the `users` field in your `config.ini` file under the `[access]` section. When you run `--process`, Quisby will automatically grant them "Editor" access to the generated Google Sheet.

```ini
[access]
users = user1@example.com,user2@example.com
```


#### **5. I'm getting an authentication error after not using Quisby for a long time. How do I fix it?**

Your Google OAuth token has likely expired. The fix is simple:

1.  Navigate to your Quisby configuration directory: `cd ~/.quisby/config/`
2.  Delete the `token.json` file: `rm token.json`
3.  Run Quisby again. It will automatically prompt you to re-authenticate through your browser, generating a new, valid token.

#### **6. How does the spreadsheet_id in config.ini work? Do I need to create the sheet first?**
You do not need to create the sheet beforehand.
* If you leave spreadsheet_id blank, Quisby will automatically create a brand new Google Sheet for you and output its ID.
* If you provide an existing spreadsheet_id, Quisby will connect to that specific sheet and update its contents. This is useful for adding data incrementally or re-running a failed process 

#### **7. What is the purpose of the charts.json file?**
The charts.json file, located in ~/.quisby/config/, acts as a local registry or cache. Quisby uses it to remember the names and IDs of the spreadsheets it has created or worked with. You should not need to edit this file manually; Quisby manages it automatically to keep track of your projects.
