from flask import Flask,render_template,redirect,request,session
from web3 import Web3,HTTPProvider
import json
from werkzeug.utils import secure_filename
import ipfsapi
import os

def connect_with_register(acc):
    web3=Web3(HTTPProvider('http://127.0.0.1:7545'))
    if acc==0:
        web3.eth.defaultAccount=web3.eth.accounts[0]
    else:
        web3.eth.defaultAccount=acc
    
    artifact_path='./build/contracts/register.json'
    with open(artifact_path) as f:
        artifact_json=json.load(f)
        contract_abi=artifact_json['abi']
        contract_address=artifact_json['networks']['5777']['address']
    
    contract=web3.eth.contract(abi=contract_abi,address=contract_address)
    return contract,web3
    
app=Flask(__name__)
app.secret_key='1234'
app.config['uploads']="uploads"
app.config['firs']="firs"


@app.route('/')
def indexPage():
    return render_template('index.html')

@app.route('/login')
def loginPage():
    return render_template('login.html')

@app.route('/adminlogin')
def adminloginPage():
    return render_template('adminlogin.html')

@app.route('/register')
def registerPage():
    return render_template('register.html')

@app.route('/registerform',methods=['post'])
def registerform():
    name=request.form['name']
    adhar=request.form['adhar']
    phone=request.form['phone']
    password1=request.form['password1']
    password2=request.form['password2']
    print(name,adhar,phone,password1,password2)
    if(password1==password2):
        try:
            contract,web3=connect_with_register(0)
            tx_hash=contract.functions.addUser(name,adhar,password1,phone).transact()
            web3.eth.waitForTransactionReceipt(tx_hash)
            return render_template('register.html',res='user added')
        except:
            return render_template('register.html',err='user already added')
    else:
        return render_template('register.html',err='Passwords didnt matched')

@app.route('/loginform',methods=['post'])
def loginform():
    adhar=request.form['adhar']
    password=request.form['password']
    print(adhar,password)
    contract,web3=connect_with_register(0)
    _names,_adhars,_passwords,_phones=contract.functions.viewUsers().call()
    for i in range(len(_names)):
        if(_adhars[i]==adhar and _passwords[i]==password):
            session['username']=adhar
            session['name']=_names[i]
            return redirect('/dashboard')
    return render_template('login.html',err='login invalid')

@app.route('/dashboard')
def dashboardpage():
    return render_template('User.html',user=session['name'])

@app.route('/logout')
def logout():
    session['username']=None
    session['name']=None
    return redirect('/')

@app.route('/raisecomplaint')
def raisecomplaint():
    return render_template('Complaint.html')

@app.route('/mycomplaints')
def mycomplaints():
    contract,web3=connect_with_register(0)
    _complaintids,_cadhars,_cnames,_complaints,_cfiles,_cstatus,_fstatus,_cfirs=contract.functions.viewComplaints().call()
    data=[]
    for i in range(len(_complaintids)):
        if(_cadhars[i]==session['username']):
            dummy=[]
            dummy.append(_complaintids[i])
            dummy.append(_complaints[i])
            dummy.append(_cfiles[i])
            if(_cstatus[i]==0):
                dummy.append(['Pending','Un-resolved'])
            if(_cstatus[i]==1):
                dummy.append(['Rejected','Un-resolved'])
            if(_cstatus[i]==2 and _fstatus[i]==0):
                dummy.append(['Accepted','Un-resolved'])
            if(_cstatus[i]==2 and _fstatus[i]==1):
                dummy.append(['Accepted','Resolved'])
            if(_cstatus[i]==2 and _fstatus[i]==2):
                dummy.append(['Accepted','Partially Resolved'])
            if(_cfirs[i]==""):
                dummy.append("NOT APPLICABLE")
            else:
                dummy.append(_cfirs[i])
            data.append(dummy)

    return render_template('view-complaints.html',name=session['name'],l=len(data),dashboard_data=data)

@app.route('/raisecomplaintform', methods=['POST'])
def raisecomplaintform():
    name = request.form['name']
    complaint = request.form['complaint']
    chooseFile=request.files['chooseFile']
    doc=secure_filename(chooseFile.filename)
    chooseFile.save('src/'+app.config['uploads']+'/'+doc)
    client=ipfsapi.Client('127.0.0.1',5001)
    print('src/'+app.config['uploads']+'/'+doc)
    response=client.add('src/'+app.config['uploads']+'/'+doc)
    print(response)
    filehash=response['Hash']
    print(filehash)
    contract,web3=connect_with_register(0)
    tx_hash=contract.functions.addComplaints(session['username'],name,complaint,filehash).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return render_template('Complaint.html', res='File Uploaded')

@app.route('/adminloginform',methods=['post'])
def adminloginform():
    wallet=request.form['wallet']
    password=request.form['password']
    print(wallet,password)
    contract,web3=connect_with_register(0)
    admin,password=contract.functions.verifyLogin().call()
    if(admin==wallet and password==password):
        return redirect('/admindashboard')
    else:
        return render_template('adminlogin.html',err='login invalid')

@app.route('/admindashboard')
def admindashboard():
    contract,web3=connect_with_register(0)
    _complaintids,_cadhars,_cnames,_complaints,_cfiles,_cstatus,_fstatus,_cfirs=contract.functions.viewComplaints().call()
    data=[]
    for i in range(len(_complaintids)):
        dummy=[]
        dummy.append(_complaintids[i])
        dummy.append(_complaints[i])
        dummy.append(_cfiles[i])
        dummy.append(_cstatus[i])
        dummy.append(_fstatus[i])
        dummy.append(_cfirs[i])
        data.append(dummy)
    return render_template('admin-dashboard.html',l=len(data),dashboard_data=data)

@app.route('/case/<id1>/<id2>')
def case(id1,id2):
    print(id1,id2)
    contract,web3=connect_with_register(0)
    tx_hash=contract.functions.updateCase(int(id1),int(id2)).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/admindashboard')

@app.route('/resolve')
def resolve():
    return render_template('resolve.html')

@app.route('/resolveform',methods=['post'])
def resolveform():
    cid=request.form['cid']
    status=request.form['status']
    chooseFile=request.files['chooseFile']
    doc=secure_filename(chooseFile.filename)
    chooseFile.save('src/'+app.config['firs']+'/'+doc)
    client=ipfsapi.Client('127.0.0.1',5001)
    print('src/'+app.config['firs']+'/'+doc)
    response=client.add('src/'+app.config['firs']+'/'+doc)
    print(response)
    filehash=response['Hash']
    print(filehash)
    contract,web3=connect_with_register(0)
    tx_hash=contract.functions.updatefir(int(cid),int(status),filehash).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return render_template('resolve.html',res='fir uploaded')

if __name__=="__main__":
    app.run(host='127.0.0.1',port=9001,debug=True)
