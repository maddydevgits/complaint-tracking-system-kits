// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract register {

  string[] _names;
  string[] _adhars;
  string[] _passwords;
  string[] _phones;

  uint[] _complaintids;
  string[] _cadhars;
  string[] _cnames;
  string[] _cfiles;
  string[] _complaints;
  uint[] _cstatus;
  uint[] _fstatus;
  string[] _cfirs;

  uint cid;
  address admin;

  constructor(){
    cid=0;
    admin=msg.sender;
  }

  mapping(string=>bool) _registeredUsers;

  function addUser(string memory name,string memory adhar,string memory password,string memory phone) public {
    require(!_registeredUsers[adhar]);

    _names.push(name);
    _adhars.push(adhar);
    _passwords.push(password);
    _phones.push(phone);
    _registeredUsers[adhar]=true;
  }

  function viewUsers() public view returns(string[] memory,string[] memory,string[] memory,string[] memory){
    return(_names,_adhars,_passwords,_phones);
  }

  function addComplaints(string memory adhaar,string memory name,string memory complaint,string memory filehash) public {
    _cadhars.push(adhaar);
    _cnames.push(name);
    _complaints.push(complaint);
    _cfiles.push(filehash);
    _cstatus.push(0);
    _cfirs.push("");
    cid+=1;
    _complaintids.push(cid);
    _fstatus.push(0);
  }

  function viewComplaints() public view returns(uint[] memory,string[] memory,string[] memory,string[] memory,string[] memory,uint[] memory,uint[] memory,string[] memory){
    return(_complaintids,_cadhars,_cnames,_complaints,_cfiles,_cstatus,_fstatus,_cfirs);
  }

  function verifyLogin() public view returns(address,string memory){
      return(admin,"1234");
  }

  function updateCase(uint complaintid,uint status) public {
    uint i;
    for(i=0;i<_complaintids.length;i++){
      if(complaintid==_complaintids[i]) {
        _cstatus[i]=status;
      }
    }
  }

  function updatefir(uint complaintid,uint status,string memory filehash) public {
    uint i;
    for(i=0;i<_complaintids.length;i++){
      if(complaintid==_complaintids[i]){
          _fstatus[i]=status;
          _cfirs[i]=filehash;
      }
    }
  }
}
