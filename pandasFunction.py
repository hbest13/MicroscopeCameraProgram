import pandas
import numpy


def func(studyUserInput, studyTrayUserInput):
    # read first csv file, this one has the corresponding "Study" and "StudyTrayId" that the user will input
    trays_data_frame = pandas.read_csv("trays.csv")

    # read the second csv file, this one has the desired filter ID values
    filters_data_frame = pandas.read_csv("trayFilters.csv")

    # studyUserInput = 'IMPROVE'
    # studyTrayUserInput = 3

    # first, check to see which study the user has entered and filter the data accordingly
    if studyUserInput == 'IMPROVE':
        # filters trays data frame for specific studies
        data_filtered_by_study = trays_data_frame.query("Study == 'IMPROVE'")

    if studyUserInput == 'CSN':
        data_filtered_by_study = trays_data_frame.query("Study == 'CSN'")

    if studyUserInput == 'Special Studies':
        data_filtered_by_study = trays_data_frame.query("Study == 'Special Study'")

    # further filter the data so that we only have rows in which the StudyTrayId matches the Tray ID entered by the user
    fully_filtered_data = data_filtered_by_study.query("StudyTrayId == @studyTrayUserInput")

    # find the study ID that corresponds with the Tray ID entered by the user
    corresponding_study_ID = int(fully_filtered_data["Id"].values[0])

    # filter the data to only have the TrayId values
    filter_collection = filters_data_frame["TrayId"].values

    # create an empty list that we will append the filter IDs to for that specific study ID
    filter_IDs = []
    print(type(filter_IDs))
    filter_positions = []
    sample_dates = []

    # loop through all the values in the dataframe containing just the TrayId values to see which one matches the
    # corresponding study ID - use the index at that row to append the corresponding filter idea to the filter ID list
    # after this code, we will be left with a list of the filter IDs for that tray
    for index, value in numpy.ndenumerate(filter_collection):
        value = value.item()
        if value == corresponding_study_ID:
            filter_IDs.append(filters_data_frame.loc[index, "FilterId"])
            filter_positions.append(filters_data_frame.loc[index, 'FilterPosition'])
            sample_dates.append(filters_data_frame.loc[index, 'SampleDate'])
    print(filter_IDs)
    print(filter_positions)
    print(sample_dates)
    return [filter_IDs, filter_positions, sample_dates]
