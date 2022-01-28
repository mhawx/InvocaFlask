import numpy as np
import pandas as pd



def googlesheet(data):


  def list_converter(string):
    if type(string)== str:
      if len(string.split(',')) < 2:
        return [string]
      else:
        return string.split(',')
    else:
      return np.nan

  data["Phone Numbers to be Swapped"] = data["Phone Numbers to be Swapped"].apply(lambda x: list_converter(x))
  data["UTM Source"] = data["UTM Source"].apply(lambda x: list_converter(x))

  data = data.explode("Phone Numbers to be Swapped")

  data = data.explode("UTM Source")

  data["Phone Numbers to be Swapped"] = data["Phone Numbers to be Swapped"].str.replace(' ', '')
  data["UTM Source"] = data["UTM Source"].str.replace(' ', '')

  data["Phone Numbers to be Swapped"] = data["Phone Numbers to be Swapped"].str.replace('\n', '')
  data["UTM Source"] = data["UTM Source"].str.replace('\n', '')

  data["Phone Numbers to be Swapped"] = data["Phone Numbers to be Swapped"].str.replace(')', ') ')
  data["UTM Source"] = data["UTM Source"].str.replace(')', ') ')

  data.drop_duplicates(keep='first')

  data = data.rename(columns={"Base URL": "url", "Phone Numbers to be Swapped": "destination", "Forward Number": "forward", "UTM Campaign":"utm_campaign", "UTM Medium":"utm_medium", "UTM Source": "utm_source","Agency": "agency"})

  return data





