# studyExtraction

## Installation
`pip install -r requirements.txt`  
`python setup.py install`

## Introduction
This tool is designed to extract data from the _in vivo_ repeat-dose toxicity (RDT) studies' database generated within the context of the [eTOX](http://www.etoxproject.eu/) project. It can work with versions 2016.1 and 2016.2. For the former, you need to request access to the data files. For the latter, you need to have the Oracle database provided by [Lhasa](https://www.lhasalimited.org/) installed and run the script from the Oracle server. Additionally, you'll need to set up the ORACLE_HOME and LD_LIBRARY_PATH environment variables.
This project is an extension of the work published in the following paper:
- [López-Massaguer O, Pinto-Gil K, Sanz F, Amberg A, Anger LT, Stolte M, Ravagli C, Marc P, Pastor M. Toxicol Sci. 2018 Mar; 162(1): 287–300.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5837688/)

## Manual
Exract studies' findings based on the given filtering and the organs' and
morphological changes' ontologies-based expansions of these findings. 

- Required arguments:
  - -a / --organ ORGAN
Anatomical entity that the finding refers to (case insensitive). You can filter for more than one organ by passing a blank space-separated list. 

- Optional arguments:
  - Version-related arguments:
    - -v / --version _{2016.1,2016.2}_
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Vitic database version (default: 2016.2).
    - -d / --sid SID
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;If working with Vitic database version 2016.2, provide the Oracle SID's.
&nbsp;&nbsp;&nbsp;&nbsp;-u / --user USER
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;If working with Vitic database version 2016.2, provide the Oracle database user name.
    - -p / --passw PASSW
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;If working with Vitic database version 2016.2, provide the Oracle database password.
  - Study design-related arguments:
    - -i / --min_exposure MIN_EXPOSURE
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Minimum exposure period (days).
    - -e / --max_exposure MAX_EXPOSURE
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Maximum exposure period (days).
    - -r / --route _{Cutaneous, Diertary, Oral, Oral gavage, Intragastric, Nasogastric, Oropharyngeal, Endotracheal, Intra-articular, Intradermal, Intraesophageal, Intraileal, Intramuscular, Subcutaneous, Intraocular, Intraperitoneal, Intrathecal, Intrauterine, Intravenous, Intravenous bolus, Intravenous drip, Parenteral, Nasal, Respiratory (inhalation), Percutaneous, Rectal, Vaginal, Subarachnoid}_
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Administration route (case insensitive). You can filter for more than one administration route by passing a blank space-separated list.
    - -s / --species _{Mouse, Rat, Hamster, Guinea pig, Rabbit, Dog, Pig, Marmoset, Monkey, Baboon}_
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Species (case insensitive). You can filter for more than one species by passing a blank space-separated list.
    - -x / --sex _{F,M,Both}_
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Study design sex.
  - Finding-related arguments:
    - -m / --observation OBSERVATION
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Morphological change type that the finding refers to (case insensitive). You can filter for more than one morphological change by passing a blank space-separated list.
    - -t / --treatment_related
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Keep only treatment-related findings.
  - Output-related arguments:
    - -o / --output_basename OUTPUT_BASENAME
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Output file base name. Two output files will be generated: basename_quant.tsv and basename_qual.tsv, with quantitative and qualitative results respectively. (default: output).

## Use examples
### 1. Extract all studies with liver-related findings
+ vitic 2016.1:  
  `python extract.py -v 2016.1 -a liver`
+ vitic 2016.2:  
  `python extract.py -v 2016.2 -d ORACLE_SID -u ORACLE_USER -p ORACLE_PASSWORD -a liver`

### 2. Extract all studies with liver- and kidney-related findings
Note that you can filter for more than one organ by passing a blank space-separated list.  
* vitic 2016.1:  
  `python extract.py -v 2016.1 -a liver kidney`  
* vitic 2016.2:  
  `python extract.py -v 2016.2 -d ORACLE_SID -u ORACLE_USER -p ORACLE_PASSWORD -a liver kidney`

### 3. Extract only studies of interest
Filter the studies of interest based on exposure time (days), administration route, and species. Note that for route and species you can filter for more than one value by passing a blank space-separated list.  
* Using long arguments:  
`python extract.py -v 2016.1 --organ liver --min_exposure 1 --max_exposure 10 --route ORAL --species MOUSE RAT`  
* Using short arguments:  
`python extract.py -v 2016.1 -a liver -i 1 -e 10 -r ORAL -s MOUSE RAT`

### 4. Extract treatment-related findings only
`python extract.py -v 2016.1 -a liver -i 1 -e 10 -r ORAL -s MOUSE RAT -t`

### 5. Output example
After extracting data using this tool, two output files are generated, one with quantitative and the other with qualitative data. Both have five common columns, namely:
- subst_id: Substance ID.
- study_count: Number of relevant studies (according to the current filering scheme) in which the substance appears.
- dose_max: Maximum dose at which the substance has been tested among the relevant studies.
- dose_min: Minimum dose at which the substance has been tested among the relevant studies.
- is_active: Boolean indicating whether the substance has been found to have any toxicity according to the current finding-related filtering criteria.

After these there is a column for each relevant finding. In these columns a value is provided if the finding is reported for the given substance, and it is empty otherwise. The value will be 1 in the qualitative file and the minimum dose at which the finding is reported in the quantitative file.

This is an example of the qualitative output: 
![qualiative](https://raw.githubusercontent.com/phi-grib/RDTextractor/master/img/qual.JPG)

This is an example of the quantitative output: 
![quantitative](https://raw.githubusercontent.com/phi-grib/RDTextractor/master/img/quant.JPG)
