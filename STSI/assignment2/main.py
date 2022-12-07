import simpy
import generators as gen #generators is a code included in the release
import numpy as np
import datetime

def main():
    
    for priority in ["FIFO", "SJF"]: # here the two priorities will be executed
        print("Processing MMn with priority {}".format(priority))
        MGn("M",priority) # memoryless processes at service for two priorities
        print('\n\n\n')
        
    print("Processing MDn")
    MGn("D", "FIFO") #deterministic process at service for FIFO discipline
    print('\n\n\n')
    
    
    print("Processing long tail") # long tail at service time
    MGn("LT", "FIFO") 
    print('\n\n\n')

def MGn(sampling, priority):
    baseLambda = 1 #arrival rate 
    rhos = [0.8,0.9,0.95] #system loads near 1
    
    serverNumbers = [1,2,4] #number of servers
    runtime = 25*baseLambda #duration of the run
    e = 0.005 #standar deviation desired for the simulation
    
    for rho in rhos: 
        for n in serverNumbers:
                        
            env = simpy.Environment() #generate the enviroment of discrete events
            start = datetime.datetime.now()
            
            mu = baseLambda/rho #capacity of the server for each load in rhos
            lambd = n*baseLambda #load of the system for each number of servers in serverNumbers
            
            print("The number of servers is now {}, load is {:.2f}".format(n,lambd/(n*mu)))
            
            server = simpy.PriorityResource(env, capacity = n) #initalization of the Resource or servers
            
            gen.queueTimes = [] # see the generator.py file, where queueTimes is a global variable. Here we initialize it as an empty array
            env.process(gen.arrival(env, lambd, mu, server, sampling, priority)) #process of and activity
            env.run(until=runtime)
            mean = np.mean(gen.queueTimes)
            
            print("Will process approximately {} arrivals".format(len(gen.queueTimes)))
            
            means = np.array([mean])
            
            std2 = 0
            j = 0
            
            std = 1
            
            while j < 99 or std > e: #loop to reach the desired standat deviation
                
                j+= 1
                
                elapsed = datetime.datetime.now()-start
                
                print('\r Processed {} out of at least 100, std is {:.3f}, elapsed time is {}'.format(j+1,std,elapsed),end=' ')
                
                env = simpy.Environment() #generate the enviroment of discrete events
                
                server = simpy.PriorityResource(env, capacity = n)
                gen.queueTimes = []
                env.process(gen.arrival(env, lambd, mu, server, sampling, priority))
                env.run(until=runtime)
                times = np.mean(gen.queueTimes)
                
                newMean = mean + (times - mean)/(j+1)
                std2 = (1-1/j)*std2 + (j+1)*(newMean - mean)**2
                mean = newMean
                std = np.sqrt(std2/j)
                
                means = np.append(means, mean)
            
            print("\n The mean is {:.3f} +- {:.3f}\n".format(mean,std*1.96))
            if runtime != 1:
                np.save("data/{}p{}s{}std{:.2f}rho{:.2f}mu{}rt{}smpl.npy".format(priority,n,e,rho,mu,runtime,sampling),means)

# set up environment and resources


# set up parameter values


# list to store queueing times


# start arrivals generator




if __name__ == "__main__":
    main()
