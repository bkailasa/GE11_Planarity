#
def isFloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def getMeas(flD):
    measH = []
    measD = {}
    endHead = False
    startMeas = False
    hl = 0
    nmeas = 0
    f=open(flD,'r')
    buffer=[]
    for l in f:
        line = l
        if (endHead):
            if (line.find("MEASUREMENT") >= 0 ):
                startMeas = True
                nmeas = nmeas + 1
                print(" Start Measurement Number ", nmeas) 
                buffer=[]
            elif(startMeas and line.find("MEAS ")>= 0):
                startMeas = False
                print(" Stop Measurement Nummber ", nmeas)
                measD[nmeas]=buffer
            elif(startMeas):
                pp = line.split()
                if (len(pp) == 2 and isFloat(pp[0])):
                    buffer.append([float(pp[0]),float(pp[1])])
                   
            
        elif (line.find("**INFO**")>0 and hl == 0):
            print ("Header Start ")
            hl = 1
        elif ((line.find("**INFO**"))>0 and (hl == 1)):
            print ("Header Stop ")
            endHead = True
            hl = 0
        elif(hl == 1):
            pp = line.split()
            if (len(pp) == 3 and isFloat(pp[0])):
                measH.append(pp)

    print ("Number of read measurement ",nmeas)
    measD[nmeas]=buffer
    print ("Verify ",len(measD))
    return measH,measD


# get the chamber to analize

import sys

if (len(sys.argv) != 2 ):
    print("Usage: ",sys.argv[0]," chamber_name")
    sys.exit(-1)
chamber_name = sys.argv[1]

print("Chamber to be analysed |","|"+chamber_name.strip())



# check how many files we have for R (readout) and D (drift)

import glob
flsR=glob.glob(chamber_name+'_R_*'+'.raw')
flsD=glob.glob(chamber_name+'_D_*'+'.raw')
print("Number of data files for the readout scan",len(flsR))
print("Number of data files for the readout scan",len(flsD))

# loop over the files and get the x,y,z values for R and D for the chamber

import ROOT
gRraw = ROOT.TGraph2D()
gRcor = ROOT.TGraph2D()
gDraw = ROOT.TGraph2D()
gDcor = ROOT.TGraph2D()


for flR in flsR:
    headReadOut,measReadOut = getMeas(flR)
    for pippo in measReadOut:        
        firsmeas = 0
        xfirs = measReadOut[pippo][firsmeas][0]
        zfirs = measReadOut[pippo][firsmeas][1]        
        print ("Scan ",pippo," Number of measures ",len(measReadOut[pippo]), " in header ",len(headReadOut))
        print ("First measurement x=",xfirs," dept=",zfirs," z= ",headReadOut[pippo-1][2])
        lastmeas = len(measReadOut[pippo])-1
        xlast = measReadOut[pippo][lastmeas][0]
        zlast = measReadOut[pippo][lastmeas][1]
        print ("Last measurement x=",xlast," dept=",zlast," z= ",headReadOut[pippo-1][2])
        tilt = (zlast - zfirs)/(xlast-xfirs)
        xmid = (xlast+xfirs)/2
        for mm in measReadOut[pippo]:
            correction = tilt*(mm[0]-xfirs)+zfirs
            gRraw.AddPoint(mm[0],float(headReadOut[pippo-1][2]),mm[1])
#           gRcor.AddPoint(mm[0],float(headReadOut[pippo-1][2]),mm[1]-correction)
            gRcor.AddPoint(-(mm[0]-xmid),float(headReadOut[pippo-1][2]),-(mm[1]-correction))   #inverted points
#            print("--> x = ",mm[0], " raw meas ",mm[1]," corrected ",mm[1]-correction)


for flD in flsD:
    headDrift,measDrift = getMeas(flD)
    for pippo in measDrift:
        firsmeas = 0
        xfirs = measDrift[pippo][firsmeas][0]
        zfirs = measDrift[pippo][firsmeas][1]        
        print ("Scan ",pippo," Number of measures ",len(measDrift[pippo]), " in header ",len(headDrift))
        print ("First measurement x=",xfirs," dept=",zfirs," z= ",headDrift[pippo-1][2])
        lastmeas = len(measDrift[pippo])-1
        xlast = measDrift[pippo][lastmeas][0]
        zlast = measDrift[pippo][lastmeas][1]
        tilt = (zlast - zfirs)/(xlast-xfirs)
        xmid = (xlast+xfirs)/2
        for mm in measDrift[pippo]:
            correction = tilt*(mm[0]-xfirs)+zfirs
            gDraw.AddPoint(mm[0],float(headDrift[pippo-1][2]),mm[1])
            gDcor.AddPoint(mm[0]-xmid,float(headDrift[pippo-1][2]),mm[1]-correction)
    
gRraw.SetTitle("Planarity for "+chamber_name+" ReadOut before correction;#\phi# (mm);#\eta# (mm);dz(mm)");
gRraw.GetHistogram().GetXaxis().SetLabelSize(0.02)
gRraw.GetHistogram().GetYaxis().SetLabelSize(0.02)
gRraw.GetHistogram().GetZaxis().SetLabelSize(0.02)
gDraw.SetTitle("Planarity for "+chamber_name+" Drift before correction;#\phi# (mm);#\eta# (mm);dz(mm)");
gDraw.GetHistogram().GetXaxis().SetLabelSize(0.02)
gDraw.GetHistogram().GetYaxis().SetLabelSize(0.02)
gDraw.GetHistogram().GetZaxis().SetLabelSize(0.02)

c1=ROOT.TCanvas("c1","Alignment raw data",20,20,800,800);
c1.Divide(2,2,0.01,0.01,0);
c1.cd(1)
gRraw.GetHistogram().GetZaxis().SetTitleOffset(0.4)
gRraw.Draw('colz')
c1.Update()
c1.cd(2)
gRraw.GetHistogram().GetXaxis().SetTitleOffset(1.3)
gRraw.GetHistogram().GetZaxis().SetTitleOffset(1.0)
gRraw.Draw('surf2')
c1.Update()
c1.cd(3)
gDraw.GetHistogram().GetZaxis().SetTitleOffset(0.4)
gDraw.Draw('colz')
c1.Update()
c1.cd(4)
gDraw.GetHistogram().GetXaxis().SetTitleOffset(1.3)
gDraw.GetHistogram().GetZaxis().SetTitleOffset(1.0)
gDraw.Draw('surf2')
c1.Update()

gRcor.SetTitle("Planarity for "+chamber_name+" ReadOut after correction;#\phi# (mm);#\eta# (mm);dz(mm)");
gRcor.GetHistogram().GetXaxis().SetLabelSize(0.02)
gRcor.GetHistogram().GetYaxis().SetLabelSize(0.02)
gRcor.GetHistogram().GetZaxis().SetLabelSize(0.02)
gDcor.SetTitle("Planarity for "+chamber_name+" Drift after correction;#\phi# (mm);#\eta# (mm);dz (mm)");
gDcor.GetHistogram().GetXaxis().SetLabelSize(0.02)
gDcor.GetHistogram().GetYaxis().SetLabelSize(0.02)
gDcor.GetHistogram().GetZaxis().SetLabelSize(0.02)

c2=ROOT.TCanvas("c2","Alignment corrected data",320,320,800,800);
c2.Divide(2,2,0.01,0.01,0);
c2.cd(1)
gRcor.GetHistogram().GetZaxis().SetTitleOffset(0.4)
gRcor.GetZaxis().SetRangeUser(0, 5);
gRcor.Draw('colz')
c2.Update()
c2.cd(2)
gRcor.GetHistogram().GetXaxis().SetTitleOffset(1.3)
gRcor.GetHistogram().GetZaxis().SetTitleOffset(1.0)
gRcor.Draw('surf2')
c2.Update()
c2.cd(3)
gDcor.GetHistogram().GetZaxis().SetTitleOffset(0.4)
gDcor.GetZaxis().SetRangeUser(-5, 0);
gDcor.Draw('colz')
c2.Update()
c2.cd(4)
gDcor.GetHistogram().GetZaxis().SetTitleOffset(1.0)
gDcor.GetHistogram().GetXaxis().SetTitleOffset(1.3)
gDcor.Draw('surf2')
c2.Update()


print("BYE")
