from Unbounce.Unbounce import retrieveUnbounceLeads

######################################################################################
#THIS IS A PROGRAM BUILT ONLY TO EXTRACT LEAD DATA FROM THE CURRENT MONTH OF OPTIMISE#
######################################################################################

#####################################
#           CONFIGURATION           #
#####################################

#INSERT YOUR API KEY HERE
api_key = 'INSERT_API_KEY_HERE'


#IF NEW PAGES, NEED TO PUT THE CODE (NOT THE NAME) OF THE PAGE INSIDE THE LIST
pages = ['PAGE 1','PAGE 2','...', 'PAGE N']


#####################################
#                END                #
#####################################

#GET VALUES AS CSV
retrieveUnbounceLeads(pages, api_key).to_csv('unbounceleads.csv', sep=',', float_format='%.0f',encoding = 'utf-8',index= False)