"""
SYST335 - Group 7
COVID-19 Queue Simulation incl. replications
"""

#importing all relevant modules
import random
import simpy
import statistics
import numpy
import pandas as pd

# initializing variables
REPLICATIONS = 1
SIMULATION_TIME = 8*60     # Simulation (e.g. 8 hour day * 60 = 480)
NUM_RECEPTIONIST = 99999  # Number of RRECEPTIONISTS in the hospital

PATIENT = (random.randint(2,4))      # generate a PATIENT at random intervals

CHECK_IN = (random.randint(1,4))      # time it takes a patient to CHECK-IN
NUM_OTHER_STAFF = 999999  # Number of OTHER STAFF (DATA GATHERING AND INPUT TO SYSTEM questionare) in the hospital
QUESTIONARE = (random.randint(2,4))      # Minutes it takes to TAKE QUESTIONARE for patient
NUM_NURSES = 5  # Number of NURSES available in the hospital
VACCINATION = (numpy.random.triangular(2,5,7))      # Minutes it takes to GET THE SHOT(vaccination) for a patient
NUM_OTHER_PERSONNEL = 99999  # Number of personnel monitoring in the Waiting Room in the hospital
WATCH_PATIENT = 0     # Minutes it takes to WATCH PARIENT AFTER VACCINATION

#initializing lists
wait_times = []
people_attended = []
time_taken_per_vaccine = []
last_patient_out_the_door = []

class Hospital(object):
#limited number of staff(receptionist, quastionare staff, nurses, doctors, other personel)
    seeded = random.sample(range(99999), 1)
    random.seed(seeded[0])
    #    def __init__(self, env, num_receptionist, check_in, num_other_staff, questionare, num_nurses, vaccination, num_other_personnel, watch_patient, num_doctors, consult):
    def __init__(self, env, num_receptionist, check_in, num_other_staff, questionare, num_nurses, vaccination, num_other_personnel, watch_patient):
        
        self.env = env
        self.receptionist = simpy.Resource(env, num_receptionist)
        self.check_in = check_in        
        self.questionare_staff = simpy.Resource(env, num_other_staff)
        self.questionare = questionare        
        self.nurses = simpy.Resource(env, num_nurses)
        self.vaccine = vaccination        
        self.other_personnel = simpy.Resource(env, num_other_personnel)
        self.waitroom = watch_patient        
#       self.doctors = simpy.Resource(env, num_doctors)
#       self.consultation_time = consult      
    #Patient gets to the hospital and reaches the receptionist
    def receptionist_check_in(self, patient):
        #time takes for check in 2 to 4 min random 
        yield self.env.timeout((random.randint(1,4)))
    #patient goes to fill the questionnaire 
    def Fill_Questionare(self, patient):
        #filling questionnaire takes 2 to 4 min
        yield self.env.timeout((random.randint(2,4)))
    #after filling the questionnaire patient goes to nurse and gets the vaccine  
    #   
    def Get_the_shot(self, patient):
        #vaccination takes 1 to 2 min with explanation of vaccine
        yield self.env.timeout(numpy.random.triangular(2,5,7))#minutes

    #patient goes to the observation room to wait for a set period of time
    def Patient_Observation(self, patient):
        #observe patients after vaccine 15 to 20 min random 
        yield self.env.timeout(WATCH_PATIENT)

'''    # we can use this code if we use doctor and time to get prescription
    def Feel_Sick(self, patient):
        #if patient feels sicke doctor prescrives medicine after examination

                    yield self.env.timeout(random.randint(4,10), CONSULT)
'''

#assign a name and number to person for event simulation
def patient(env, name, hp):
    print('%s arrives at the hospital at %.2f.' % (name, env.now))
    with hp.receptionist.request() as request:
        yield request
        walk1 = env.now
        #print('%s enters the Reception Desk at %.2f.' % (name, walk1))
        yield env.process(hp.receptionist_check_in(name))
        wait1 = env.now - walk1
        #print('%s Registers and leaves the reception desk at %.2f. Stayed for %.2f.' % (name, env.now, wait1))                       
    #print('%s walks to the Q staff at %.2f.' % (name, env.now))
    with hp.questionare_staff.request() as request:
        yield request
        arrive2 = env.now
        #print('%s Fills the Q at %.2f.' % (name, env.now))
        yield env.process(hp.Fill_Questionare(name))
        wait2 = env.now - arrive2
        #print('%s leaves the Questionare Staff at %.2f. Stayed for %.2f.' % (name, env.now, wait2))
    #print('%s arrives at the Nurses Stationl at %.2f.' % (name, env.now))
    with hp.nurses.request() as request:
        yield request
        arrive3 = env.now
        #print('%s gets the Vaccine and Explanation with the nurse at %.2f.' % (name, env.now))
        yield env.process(hp.Get_the_shot(name))
        wait3 = env.now - arrive3
        print('The vaccine took %.2f.' % (wait3))
        print('%s leaves the Nurses Station at %.2f. Stayed for %.2f.' % (name, env.now, wait3))
        time_taken_per_vaccine.append(wait3)        
              

        # Find how many patients got their vaccines
        s = name
        last_patient_out_the_door.append([s.replace('Patient ', '')])

    #print('%s arrives at the Waiting Room at %.2f.' % (name, env.now))
    with hp.other_personnel.request() as request:
        yield request
        arrive4 = env.now
        #print('%s Sits at the Waiting Room at %.2f.' % (name, env.now))
        yield env.process(hp.Patient_Observation(name))
        wait4 = env.now - arrive4
        print('%s leaves the Waiting Room at %.2f. Stayed for %.2f.' % (name, env.now, wait4))
        TotalWait = wait1 + wait2 + wait3 + wait4
        wait_times.append(TotalWait)



        #print('%s LEAVES THE HOSPITAL AT %.2f. Stayed for %.2f.--------------------------------' % (name, env.now, TotalWait))  
    if env.now >= 480:
        yield env.timeout()


# we can defer to use the following part and and assume all patients are well after vaccination 
'''
    print('%s arrives at the Doctors Room at %.2f.' % (name, env.now))
    if random.choice([True, False]):
        with hp.doctors.request() as request:
            yield request
            print('%s gets a prescription at %.2f.' % (name, env.now))
            yield env.process(hp.Feel_Sick(name))
    else:
            wait5 = env.now - walk1
            wait_times.append(wait5)
            print('%s LEAVES THE HOSPITAL AT %.2f. Stayed for %.2f.--------------------------------' % (name, env.now, wait5))
'''            

#def setup(env, num_receptionist, check_in, p_inter, num_other_staff, questionare, num_nurses, vaccination, num_other_personnel, watch_patient, num_doctors, consult):
def setup(env, num_receptionist, check_in, p_inter, num_other_staff, questionare, num_nurses, vaccination, num_other_personnel, watch_patient):

# Create the hospital
   # hospital = Hospital(env, num_receptionist, check_in, num_other_staff, questionare, num_nurses, vaccination, num_other_personnel, watch_patient, num_doctors, consult)
    hospital = Hospital(env, num_receptionist, check_in, num_other_staff, questionare, num_nurses, vaccination, num_other_personnel, watch_patient)
    
    # Create 10 patients to start
    for i in range(999,1000):
        env.process(patient(env, 'Patient %d' % i, hospital))
    # generating patients while running simulation
    while True:
        x = numpy.random.poisson(5,100)
        y = x[0]
        yield env.timeout(y)
        i += 1
        env.process(patient(env, 'Patient %d' % i, hospital))

def avg_total_time_for_visit(wait_times):
    avg_wait = statistics.mean(wait_times)
    minutes, frac_minutes = divmod(avg_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds) 

def avg_wait_time2(time_taken_per_vaccine):
    avg_wait = statistics.mean(time_taken_per_vaccine)
    minutes, frac_minutes = divmod(avg_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds) 

def summ_people(name):
    Sum = sum(name)
    return Sum

#SIMULATION STARTS HERE

minute1 = []
minute2 = []
seconds1 = []
seconds2 = []
master_list = []
simulation_list = []

for i in range(REPLICATIONS):#the number of times the program runs
    print('Hospital Run', i)
    
    # Do not generate the same results
    seeded = random.sample(range(99999), 1)
    random.seed(seeded[0])
    
    env = simpy.Environment()
    env.process(setup(env, NUM_RECEPTIONIST, CHECK_IN, PATIENT, NUM_OTHER_STAFF, QUESTIONARE, NUM_NURSES, VACCINATION, NUM_OTHER_PERSONNEL, WATCH_PATIENT))
#use line below if we are using all parameters not greyed out
#env.process(setup(env, NUM_RECEPTIONIST, CHECK_IN, PATIENT, NUM_OTHER_STAFF, QUESTIONARE, NUM_NURSES, VACCINATION, NUM_OTHER_PERSONNEL, WATCH_PATIENT, NUM_DOCTORS, CONSULT))
    env.run(until=SIMULATION_TIME)


#total wait_times overall_visit_time for whole visit 
    mins1, secs1 = avg_total_time_for_visit(wait_times)
    print("Statistical analysis in progress...", f"\nThe average total time for the whole visit is {mins1} minutes and {secs1} seconds.")

#total time_taken_per_vaccine 
    mins2, secs2 = avg_wait_time2(time_taken_per_vaccine)
    print("Statistical analysis in progress...", f"\nThe average waiting time for Vaccine administration is {mins2} minutes and {secs2} seconds.")
    print(wait_times)
    minute1.append(mins1)
    minute2.append(mins2)
    seconds1.append(secs1)
    seconds2.append(secs2)
    print(' ')
    print(' ')
    print('------------------------------------------------------------------------------------------------')
    print(' ')
    print(' ')
    print('average total time for the whole visit minutes plus seconds')
    a = minute1
    b = seconds1
    re = [x + y/100 for x,y in zip(a,b)]
    print(re)
    print(' ')

    print('average waiting time for Vaccine administration minutes plus seconds')
    c = minute2
    d = seconds2
    re2 = [x + y/100 for x,y in zip(c,d)]
    print(re2)

#print number of patients who got vaccinated before waiting room
    convertme = [[int(num) for num in sub] for sub in last_patient_out_the_door]
    sssss = max(convertme, key=lambda x:int(x[0]))
    max_patients = sssss[0]
    master_list.append(max_patients)

print(master_list)


# saving the dataframe
w=re
s=re2
dict = {'Total number of patients': master_list,    
        'Total_Time_in_Hospital_(avg)':w, 
        'Time_for_Vaccine_(avg)':s}

df = pd.DataFrame(dict)
df.to_csv('VaccineRun.csv', index = False, header=True)

print (df)

filename = 'arena.txt'

with open(filename, mode="w") as outfile:
    for s in wait_times:
        outfile.write("%s\n" % s)