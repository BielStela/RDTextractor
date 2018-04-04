#!/usr/bin/env python
#! -*- coding: utf-8 -*-

##    Description    eTOX repeat-dose toxicity extraction tool
##
##    Authors:       Elisabet Gregori (elisabet.gregori@upf.edu)
##                   Ignacio Pasamontes (ignacio.pasamontes@upf.edu)
##
##    Copyright 2018 Elisabet Gregori & Ignacio Pasamontes
##
##    studyExtraction is free software: you can redistribute it 
##    and/or modify it under the terms of the GNU General Public 
##    License as published by the Free Software Foundation version 3.
##
##    studyExtraction is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this code. If not, see <http://www.gnu.org/licenses/>.

import argparse, os, sys, time, math
import pandas as pd
# Disable SettingWithCopyWarning warnings
pd.set_option('chained_assignment', None)
import cx_Oracle

# Load ontology dataframe
onto_file = 'ontology.pkl'
fname = os.path.join(os.path.dirname(__file__), 'data',  onto_file)
onto_df = pd.read_pickle(fname)

def load_version(args):

    """
    Load tables with information
    """

    if args.version == '2016.1':
        ########################## 
        # Load stored dataframes #
        ##########################

        # Load study dataframe
        study_file = 'study.pkl'
        fname = os.path.join(os.path.dirname(__file__), 
                            'data',  study_file)
        study_df = pd.read_pickle(fname)
        # Load finding dataframe
        find_file = 'findings.pkl.gz'
        fname = os.path.join(os.path.dirname(__file__), 
                            'data',  find_file)
        find_df = pd.read_pickle(fname, compression='gzip')
    else:
        #########################################
        # Query the Oracle database to generate #
        # the dataframes                        #
        #########################################

        # Load normlisation lookup table
        norm_file = 'normalisation.pkl'
        fname = os.path.join(os.path.dirname(__file__), 
                            '../data',  norm_file)
        normD = pd.read_pickle(fname)

        dsn_tns = cx_Oracle.makedsn('localhost', '1521', args.sid)

        con = cx_Oracle.connect(args.user, args.passw)
        cur = con.cursor()

        # Generate normalised study dataframe
        sys.stdout.write('\tLoading studies\n')
        cmd = "SELECT SUBST_ID, SUBST_ID, STANDARDISED_SEX, STANDARDISED_ROUTE, \
            STANDARDISED_SPECIES, EXPOSURE_PERIOD \
            FROM STUDY_DESIGN \
            JOIN SUBSTANCE_IDS ON STUDY_DESIGN.STRUCTURE_LUID = SUBSTANCE_IDS.LUID"
        cur.execute(cmd)
        results = cur.fetchall()
        tmp_table = []
        for (study_id, subst_id, sex, route, species, exposure) in results:
             sex = sex.upper()
             sex = normD[sex]
             if route is None:
                 route = ''
             else:
                 route = route.upper()
                 route = normD[route]
             if species is None or species.upper() in ('EXCLUDED TERM'):
                 species = ''
             else:
                 species = species.upper()
                 species = normD[species]
             tmp_table.append([study_id, subst_id, sex, route, species, exposure])
        study_df = pd.DataFrame(tmp_table, columns=['study_id', 'subst_id', 'normalised_sex',
                        'normalised_administration_route', 'normalised_species', 'exposure_period_days'])

        # Generate normalised findings dataframe
        sys.stdout.write('\tLoading findings\n')
        cmd = "SELECT DISTINCT PARENT_LUID AS study_id, RELEVANCE, \
            STANDARDISED_PATHOLOGY, STANDARDISED_ORGAN, DOSE \
            FROM HISTOPATHOLOGICALFI \
            WHERE STANDARDISED_PATHOLOGY IS NOT NULL \
            AND STANDARDISED_ORGAN IS NOT NULL"
        cur.execute(cmd)
        results = cur.fetchall()
        tmp_table = []
        for (study_id, relevance, observation, organ, dose) in results:
             if observation is None or observation.upper() == 'EXCLUDED TERM':
                 observation = ''
             else:
                 observation_upper = observation.upper()
                 if observation_upper in normD:
                     observation = normD[observation_upper]
 
             if organ is None or organ.upper() == 'EXCLUDED TERM':
                 organ = ''
             else:
                 organ_upper = organ.upper()
                 if organ_upper in normD:
                     organ = normD[organ_upper]
             
             if relevance is None:
                 relevance = 'NA'
             tmp_table.append([study_id, relevance, observation, organ, dose])
        
        cmd = "SELECT DISTINCT PARENT_LUID AS study_id, RELEVANCE, \
            FINDING, DOSE \
            FROM CLINICALCHEMICALFIN"
        cur.execute(cmd)
        results = cur.fetchall()
        for (study_id, relevance, observation, dose) in results:
             if observation is None or observation.upper() == 'EXCLUDED TERM':
                 observation = ''
             else:
                 observation_upper = observation.upper()
                 if observation_upper in normD:
                     observation = normD[observation_upper]
             organ = ''

             if relevance is None:
                 relevance = 'NA'
             tmp_table.append([study_id, relevance, observation, organ, dose])

        cmd = "SELECT DISTINCT PARENT_LUID AS study_id, RELEVANCE, \
            FINDING, DOSE \
            FROM CLINICALHEMATOLOGIC"
        cur.execute(cmd)
        results = cur.fetchall()
        for (study_id, relevance, observation, dose) in results:
             if observation is None or observation.upper() == 'EXCLUDED TERM':
                 observation = ''
             else:
                 observation_upper = observation.upper()
                 if observation_upper in normD:
                     observation = normD[observation_upper]
             organ = ''

             if relevance is None:
                 relevance = 'NA'
             tmp_table.append([study_id, relevance, observation, organ, dose])

        cmd = "SELECT DISTINCT PARENT_LUID AS study_id, RELEVANCE, \
            FINDING, STANDARDISED_ORGAN, DOSE \
            FROM ORGAN_WEIGHTS"
        cur.execute(cmd)
        results = cur.fetchall()
        for (study_id, relevance, observation, organ, dose) in results:
             if observation is None or observation.upper() == 'EXCLUDED TERM':
                 observation = ''
             else:
                 observation_upper = observation.upper()
                 if observation_upper in normD:
                     observation = normD[observation_upper]

             if organ is None or organ.upper() == 'EXCLUDED TERM':
                 organ = ''
             else:
                 organ_upper = organ.upper()
                 if organ_upper in normD:
                     organ = normD[organ_upper]

             if relevance is None:
                 relevance = 'NA'
             tmp_table.append([study_id, relevance, observation, organ, dose])

        find_df = pd.DataFrame(tmp_table, columns=['study_id', 'relevance',
                        'observation_normalised', 'organ_normalised', 'dose'])

        con.close()

    if args.treatment_related:
        find_df = find_df[find_df.relevance == 'treatment related']

    return study_df,find_df

def filter_study(args,study_df):
    """
    """
    df = study_df[:]

    # Exposure
    if args.min_exposure is not None and args.max_exposure is not None:
        # An exposure range filter is defined
        df = df[df.exposure_period_days >= args.min_exposure &
                df.exposure_period_days <= args.max_exposure]
    elif args.min_exposure is not None:
        # Only a.upper bound for exposure range has been set
        df = df[df.exposure_period_days >= args.min_exposure]
    elif args.max_exposure is not None:
        df = df[df.exposure_period_days <= args.max_exposure]

    # Administration route
    if args.route:
        df = df[df.normalised_administration_route.str.lower().isin([x.lower() for x in args.route])]
        
    # Species
    if args.species:
        df = df[df.normalised_species.str.lower().isin([x.lower() for x in args.species])]
        
    # Study's level sex
    if args.sex:
        df = df[df.normalised_sex.str.lower() == args.sex.lower()]
    
    return df

def expand(df,args):

    """
    Expand standardized observation and normalized organs based on
    the hierarchy of ontologies stored in onto_df
    """
    # Create an empty output dataframe
       
    #########
    # ORGAN #
    #########
    organs_dict={}
    all_organs=set()
    for organ in args.organ:    
        all_related_organs = set([organ])
        related_organs = onto_df[(onto_df.parent_term == organ) & 
                            (onto_df.ontology == 'anatomy')]
        all_related_organs = all_related_organs.union(related_organs.child_term)
    
        while not related_organs.empty:
            related_organs = onto_df[(onto_df.parent_term.isin(related_organs.child_term)) & 
                                (onto_df.ontology=='anatomy')]
            all_related_organs = all_related_organs.union(related_organs.child_term)
    
        organs_dict.update({n: organ for n in all_related_organs})
        all_organs = all_organs.union(all_related_organs,all_organs)
    
    df = df[df['organ_normalised'].isin(all_organs)]
    df.loc[:,'organ_normalised'] = df['organ_normalised'].map(organs_dict)

   
    ###############
    # OBSERVATION #
    ###############
    if args.observation is None:

        obs_list=[]
       
        for row in df.to_dict('records'):
           
            obs_list.append(row)

            parents=onto_df[(onto_df['child_term'] == row['observation_normalised']) & 
                        (onto_df['ontology'] == 'histopathology')  & (onto_df['parent_term']!="morphologic change")]

            while not parents.empty:
                new_parents = []
                #Add new row to the dataframe with the name of the parent 
                for parent in parents.parent_term:
                    new_row=row.copy()
                    new_row['observation_normalised'] = parent
                    obs_list.append(new_row)
                    new_parents.append(parent)

                parents = onto_df[(onto_df['child_term'].isin(new_parents))
                            & (onto_df['ontology'] == 'histopathology') 
                            & (onto_df['parent_term']!="morphologic change")]
       
        findings_out = df.from_dict(obs_list)
        findings_out.drop_duplicates(inplace=True)
        
    else:
        observation_dict = {}
        all_observations = set()
        for observation in args.observation:
    
            all_related_observation = set([observation])
            related_observation = onto_df[(onto_df.parent_term == observation) 
                                        & (onto_df.ontology == 'histopathology')]
            all_related_observation = all_related_observation.union(related_observation.child_term)
    
            while not related_observation.empty:
            
                related_observation = onto_df[(onto_df.parent_term.isin(related_observation.child_term)) 
                                    & (onto_df.ontology=='histopathology')]
                all_related_observation = all_related_observation.union(related_observation.child_term)
    
            observation_dict.update({n: organ for n in all_related_observation})
            all_observations = all_organs.union(all_related_observation,all_observation)
    
        findings_out=df[df['observation_normalised'].isin(all_organs)]
        findings_out.loc[:,'observation_normalised']=df['observation_normalised'].map(organs_dict)

    
    return findings_out

def get_stats(group):
    return {'min': group.min(), 'max': group.max()}

def run(args):

    """
    Run the data extraction based on the parsed filters and expanding
    based on the organs and morphological changes ontologies.
    """

    sys.stderr.write('\nLoading background information for version %s\n' %args.version)
    study_df, find_df = load_version(args)
    
    #################################
    # Select only relevant findings #
    #################################
    sys.stderr.write('Filtering to relevant information\n')
    relevant_studies_df = filter_study(args,study_df)
    relevant_find = find_df[find_df.study_id.isin(relevant_studies_df.study_id)]
    relevant_find = pd.merge(relevant_find, study_df[['study_id', 'subst_id']],
                        how='left', on='study_id', left_index=False,
                        right_index=False, sort=False)
    
    ###################################
    # Get stats for relevant findings #
    ###################################
    # Get the number of studies per substance
    count_df = relevant_find.groupby(('subst_id')).study_id.nunique().to_frame().reset_index()
    # Get the global dose range per substance
    range_df = relevant_find[relevant_find.dose > 0]
    range_df = range_df.groupby(('subst_id')).dose.apply(get_stats).unstack().reset_index()
    # Get all stats into a single dataframe
    stats_df = pd.merge(count_df, range_df, how='inner', on='subst_id', 
                        left_index=False, right_index=False, sort=False)
    stats_df.columns = ['subst_id', 'study_count', 'dose_max', 'dose_min']

    ###################################################################
    # Expand based on anatomical and morphological changes ontologies #
    ###################################################################
    # Expand organs and histopathological findings according to the ontologies 
    # and filter by finding-based arguments
    sys.stderr.write('Expand based on anatomic and morphological change ontologies\n')
    filtered_find = expand(relevant_find,args)

    if filtered_find.empty:
        raise Exception('Filtered out all rows, so the dataframe is empty.')

    ######################################
    # Aggragate by substance and finding #
    ######################################
    # Define finding as organ+observation
    filtered_find.organ_normalised = filtered_find.organ_normalised.fillna('NA')
    filtered_find.observation_normalised = filtered_find.observation_normalised.fillna('NA')
    filtered_find['finding'] = filtered_find.apply(lambda row: row.organ_normalised+'_'+row.observation_normalised, axis=1)
    filtered_find = filtered_find[['subst_id', 'finding', 'dose']]

    # Aggregate by substance and finding (as defined above), keeping the minimum dose 
    # for each substance/finding instance
    group_df = filtered_find.groupby(('subst_id', 'finding')).min().add_prefix('min_').reset_index()
    
    #######################################
    # Pivot so that each finding is a row #
    #######################################
    ### Quantitative
    pivotted_df = group_df.pivot_table(index='subst_id', columns='finding', values='min_dose').reset_index()
    pivotted_df['is_active'] = 'True'
    quantitative_df = pd.merge(stats_df, pivotted_df, how='left', on='subst_id', 
                                left_index=False, right_index=False, sort=False)
    quantitative_df.is_active = quantitative_df.is_active.fillna('False')
    # Reorder columns
    cols = quantitative_df.columns.tolist()
    cols = cols[0:4]+[cols[-1]]+cols[4:-1]
    quantitative_df = quantitative_df[cols]
    
    ### Qualitative
    group_df.loc[:,'min_dose'] = 1
    pivotted_df = group_df.pivot_table(index='subst_id', columns='finding', values='min_dose').reset_index()
    pivotted_df['is_active'] = 'True'
    qualitative_df = pd.merge(stats_df, pivotted_df, how='left', on='subst_id',
                                left_index=False, right_index=False, sort=False)
    qualitative_df.is_active = qualitative_df.is_active.fillna('False')
    # Reorder columns
    cols = qualitative_df.columns.tolist()
    cols = cols[0:4]+[cols[-1]]+cols[4:-1]
    qualitative_df = qualitative_df[cols]

    ####################
    # Save the results #
    ####################
    quantitative_df.to_csv(args.output_basename+'_quant.tsv', 
                            sep='\t', index=False)
    qualitative_df.to_csv(args.output_basename+'_qual.tsv', 
                            sep='\t', index=False)

def main ():
    """
    Parse arguments and load the extraction filters.
    """
    parser = argparse.ArgumentParser(description='Exract studies\' \
            findings based on the given filtering and the organs\' and \
            morphological changes\' ontologies-based expansions of these \
            findngs.')

    # Version-related arguments
    parser.add_argument('-v', '--version', help='Vitic database version \
            (default: 2016.2).', 
            choices=['2016.1', '2016.2'], default= '2016.2', required=False)
    parser.add_argument('-d', '--sid', help='If working with Vitic \
            database version 2016.2, provide the Oracle SID\'s.', 
            required=False)
    parser.add_argument('-u', '--user', help='If working with Vitic \
            database version 2016.2, provide the Oracle database \
            user name.', required=False)
    parser.add_argument('-p', '--passw', help='If working with Vitic \
            database version 2016.2, provide the Oracle database \
            password.',  required=False)

    # Study-related arguments
    parser.add_argument('-i', '--min_exposure', help='Minimum exposure \
            period (days).', required=False)
    parser.add_argument('-e', '--max_exposure', help='Maximum exposure \
            period (days).', required=False)
    parser.add_argument('-r', '--route', help='Administration route. You can filter for \
            more than one administration route by passing a blank space-separated list.', 
            choices=['cutaneous', 'diertary', 'oral', 'oral gavage', 
            'intragastric', 'nasogastric', 'oropharyngeal', 'endotracheal', 
            'intra-articular', 'intradermal', 'intraesophageal', 
            'intraileal', 'intramuscular', 'subcutaneous', 'intraocular', 
            'intraperitoneal', 'intrathecal', 'intrauterine', 
            'intravenous', 'intravenous bolus', 'intravenous drip', 
            'parenteral', 'nasal', 'respiratory (inhalation)', 
            'percutaneous', 'rectal', 'vaginal', 'subarachnoid'], 
            type= str.lower,
            # nargs='*' is used to allow to pass a list (separated by 
            # blank spaces) as the argument 
            # '*' -> 0 or more
            # '+' -> 1 or more
            nargs='*', required=False)
    parser.add_argument('-s', '--species', help='Species. You can filter for \
            more than one species by passing a blank space-separated list.', 
            choices=['mouse', 'rat', 'hamster', 'guinea pig', 'rabbit', 'dog', 
            'pig', 'marmoset', 'monkey', 'baboon'], type= str.lower,
            nargs='*', required=False)
    parser.add_argument('-x', '--sex', help='Study design sex.', 
            choices=['F', 'M', 'Both'], required=False)

    # Finding-related arguments
    parser.add_argument('-a', '--organ', help='Anatomical entity that the \
            finding refers to. You can filter for more than one organ by passing \
            a blank space-separated list.', type= str.lower,
            nargs='*', required=True)
    parser.add_argument('-m', '--observation', help='Morphological change \
            type that the finding refers to. You can filter for more than one \
            morphological change by passing a blank space-separated list.', type= str.lower,
            nargs='*', required=False)
    parser.add_argument('-t', '--treatment_related', help='Keep only treatment-related \
            findings.', action='store_true', default= False,
            required=False)
    
    # Output file base name
    parser.add_argument('-o', '--output_basename', help='Output file base name. Two output \
            files will be generated: basename_quant.tsv and basename_qual.tsv, with \
            quantitative and qualitative results respectively. (default: output).', 
            default= 'output', required=False)

    args = parser.parse_args()
    if args.version == '2016.2' and args.passw is None:
       raise argparse.ArgumentTypeError('Oracle database password required to work \
                                        with version 2016.2.')

    if args.observation:
        right_case_observations = []
        for obs in args.observation:
            right_case_obs =  list(onto_df[onto_df['parent_term'].str.lower() == obs].parent_term.unique())
            if len(right_case_obs) == 0:
                sys.stderr.write('The observation %s is not found in the database.\n' %obs)
            else:
                right_case_observations.extend(right_case_obs)
        if len(right_case_observations) == 0:
            raise argparse.ArgumentTypeError('None of the observations you are trying \
                                            to filter for are found: %s.' %args.observation)
        args.observation = right_case_observations

    right_case_organs = []
    for org in args.organ:
        right_case_obs =  list(onto_df[onto_df['parent_term'].str.lower() == org].parent_term.unique())
        if len(right_case_obs) == 0:
            sys.stderr.write('The organ %s is not found in the database.\n' %org)
        else:
            right_case_organs.extend(right_case_obs)
    if len(right_case_organs) == 0:
        raise argparse.ArgumentTypeError('None of the organs you are trying to filter \
                                        for are found: %s.' %args.organ)
    args.organ = right_case_organs

    run(args)

if __name__ == '__main__':    
    main()
