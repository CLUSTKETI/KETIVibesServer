window.indexedDB = window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB || window.msIndexedDB;
let db;

let indexedDB = {


// 인덱스 디비 열기
    openIndexedDB : () => {
  
    let req = indexedDB.open('stepDB', 1);
    
    req.onsuccess = function (evt) {   
      db = req.result;
      console.log("openDb DONE");
    };
  
    req.onerror = function (evt) {
      console.error("openDb:", evt.target.errorCode);
    };
  
    req.onupgradeneeded = function (evt) {
      console.log("openDb.onupgradeneeded");    
      let objectStore = evt.currentTarget.result.createObjectStore('stepStore', { keyPath: "blockId" });
      objectStore.createIndex("step", "step", { unique: false });
    };
  }
  
  //데이터 저장하기
  , saveCurrentIndex : (p_block = 1, p_step) => {  
   
    let objectStore = getObjectStore('stepStore', 'readwrite');
    let request   = objectStore.get(p_block);
  
    request.onerror = function(event) {
      console.error("updateIndexData onerror");
    };
  
    request.onsuccess = function(event) {
      // Get the old value that we want to update
      console.log("updateIndexData onsuccess");
        //데이터가 없으면 save, 있으면 update
      let data = event.target.result;
  
      if (data == undefined){
        let requestInsert = objectStore.add({blockId : p_block, step : p_step});
        requestInsert.onerror = function(event) {
          // Do something with the error
          console.error("requestInsert onerror");
        };
        requestInsert.onsuccess = function(event) {
          // Success - the data is updated!
          console.log("requestInsert onsuccess");
        };
  
      }else{
        data.step = p_step;
        let requestUpdate = objectStore.put(data);
  
        requestUpdate.onerror = function(event) {
          // Do something with the error
          console.error("requestUpdate onerror");
        };
        requestUpdate.onsuccess = function(event) {
          // Success - the data is updated!
          console.log("requestUpdate onsuccess");
        };
      }
    
  
      
    };
  
   
  
  }
  
  //데이터 삭제하기
  ,deleteIndexData : (d) => {
    let request = db.transaction(["stepDB"], "readwrite").objectStore("stepStore").delete(d);
  
    request.onsuccess = function (e) {
      console.log("deleteIndexData onsuccess");
    };
  
    request.onerror = function (e) {
      console.error("deleteIndexData onerror");
    };
  
  }
  
  //데이터 가져오기
  , getIndexData : (d) => {
    let objectStore   = getObjectStore('stepStore', 'readwrite');
    let request   = objectStore.get(d);
    
    request.onerror = function (event) {
      console.error("getIndexData onerror");
      // Handle errors!
    };
    request.onsuccess = function (event) {
      
      let result = event.currentTarget.result;    
      $("#steplevel_" + d).val(result.step);
  
  
      // Do something with the request.result!
      //alert("Name for SSN 444-44-4444 is " + request.result.name);
    };
  
  
  }
  
  //스토어 클리어
  , clearObjectStore : () => {
    let store = getObjectStore('stepStore', 'readwrite');
    let req = store.clear();
  
    req.onsuccess = function(evt) {
      console.log("clearObjectStore onsuccess");
    };
    req.onerror = function (evt) {
      console.error("clearObjectStore:", evt.target.errorCode);
   
    };
  }
  
  , getObjectStore : (store_name, mode) => {
  
    let tx = db.transaction(store_name, mode);
    
    return tx.objectStore(store_name);
  
  }
  
  , removeIndexedDB : () => {
    let req = indexedDB.deleteDatabase("stepDB");
  
    req.onsuccess = function () {
        console.log("Deleted database successfully");
    };
    req.onerror = function () {
        console.error("Couldn't delete database");
    };
    req.onblocked = function () {
        console.error("Couldn't delete database due to the operation being blocked");
    };
  }
  
  


}