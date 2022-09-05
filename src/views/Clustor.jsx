import { lazy } from "react";
import { useState, useEffect } from "react";
import {useParams} from "react-router-dom";


import {fetchStorage, fetchSupply, fetchLocked,  fetchTokenMetaData} from "../utils/tzkt"
import {initOperation, issueOperation, redeemOperation, lockOperation, unlockOperation, approveOperation, flashOperation} from "../utils/operations"

const TokensList = lazy(() => import("../components/TokensList"));

let ListAddresses = [];

const Clustor = () => {

    const {address} = useParams();

    const [ctokenAddress, setCTokenAddress] = useState("");       
    const [loading, setLoading] = useState(false);
    const [clustorStatus, setClustorStatus] = useState(false);
    const [lockedClustors, setLockedClustors] = useState(0);
    const [totalSupply, setTotalSupply] = useState(0);
    const [name, setName] = useState("");

    const [flashAmount, setFlashAmount] = useState(0);
    const [flashAddress, setFlashAddress] = useState("");
    const [tokenFlash, setTokenFlash] = useState("");

    const [amount, setAmount] = useState(1);

    useEffect(() => {
        (async () => {
            const storage = await fetchStorage(address);
            const supply = await fetchSupply(storage.clustorToken);
            const tokenMap = await storage.tokens;
            
            for (const token in tokenMap) {
                let metadata = await fetchTokenMetaData(token);
                ListAddresses.push({sym : metadata.sym, address : token, value : (tokenMap[token] / Math.pow(10, metadata.dec)), raw_value : tokenMap[token]});           
            }      

            setTotalSupply(supply);
            setClustorStatus(storage.clustorInited);
            setName(storage.clustorName);   
            setLockedClustors(Number(storage.lockedClustors));  
            setCTokenAddress(storage.clustorToken);   
        })();
            return () => {
            ListAddresses = [];
            setTotalSupply(0);
            setClustorStatus(false);
            setLockedClustors(0);
            setName("Clustor Name");
        }
    }, []) // eslint-disable-line react-hooks/exhaustive-deps

      const onInit = async () => {
        try {
          setLoading(true);
          await initOperation(address);
          alert("Transaction succesful!");
        } catch (err) {
          alert(err.message);
        }
        setLoading(false);
        const fstorage = await fetchStorage(address);
        setLockedClustors(Number(fstorage.lockedClustors));
        const fsupply = await fetchSupply(fstorage.clustorToken);
        setTotalSupply(fsupply);
      }
  
    const onIssue = async () => {
        try {
          setLoading(true);
          await issueOperation(address, amount);
          alert("Transaction succesful!");
        } catch (err) {
          alert(err.message);
        }
        setLoading(false);  
        const fsupply = await fetchSupply(ctokenAddress);
        setTotalSupply(fsupply);      
    }

    const onRedeem = async () => {
        try {
          setLoading(true);
          await redeemOperation(address, amount);
          alert("Transaction succesful!");
        } catch (err) {
          alert(err.message);
        }
        setLoading(false);  
        const fsupply = await fetchSupply(ctokenAddress);
        setTotalSupply(fsupply);     
    }   

    const onLock = async () => {
        try {
          setLoading(true);
          await lockOperation(address, amount);
          alert("Transaction succesful!");
        } catch (err) {
          alert(err.message);
        }
        setLoading(false);
        const locked = await fetchLocked(address);
        setLockedClustors(locked);        
    } 

    const onUnlock = async () => {
        try {
          setLoading(true);
          await unlockOperation(address, amount);
          alert("Transaction succesful!");
        } catch (err) {
          alert(err.message);
        }
        setLoading(false);
        const locked = await fetchLocked(address);
        setLockedClustors(locked);        
    }

    const onApprove = async () => {
        try {
          setLoading(true);
          for(const i in ListAddresses){
                await approveOperation(ListAddresses[i].address, address , ListAddresses[i].raw_value * amount );
                alert("Transaction succesful!");
           }
        } catch (err) {
          alert(err.message);
        }
        setLoading(false);
        const locked = await fetchLocked(address);
        setLockedClustors(locked);        
    }

    const onFlash = async () => {
        try {
          setLoading(true);
          await flashOperation(address, tokenFlash, flashAddress, flashAmount);
        } catch (err) {
          alert(err.message);
        }
        setLoading(false);     
    }


    return (
        <div className="">
           <h1 className="mb-4 text-4xl flex justify-center align-middle font-bold text-gray-700 md:text-2xl lg:text-4xl ">{name}</h1>
          {clustorStatus ?
            <div className="wrapper">
            <h3 className="mb-4 text-lg flex justify-center align-middle font-semibold text-gray-700 md:text-xl lg:text-xl">{"Clustor Supply : " + totalSupply}</h3>
            <span className="mb-2 cursor-text text-sm flex justify-center align-middle font-normal text-gray-600 lg:text-m sm:px-16 xl:px-48 dark:text-gray-600">{"Clustor Address : " + ctokenAddress}</span>
            <span className="mb-2 text-sm flex justify-center align-middle font-normal text-gray-600 lg:text-m sm:px-16 xl:px-48 dark:text-gray-600">Add this token address to your respective wallets</span>
          </div>
          :
            <button className="py-2.5 px-5 mr-2 text-sm font-medium text-gray-900 bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 inline-flex items-center" onClick={onInit}>{loading ? "Loading...":"Initialize"}
            </button>
          }
        
          <div className="flex flex-row justify-center align-middle">

            <div className="w-5/12">
              <h3 className="mb-4 flex justify-center align-middle text-2xl font-bold tracking-tight leading-none text-gray-700 md:text-xl lg:text-2xl">Token List</h3>
              <TokensList addresses={ListAddresses} />
              <div className="flex justify-center align-middle">
              <div className="flex justify-center align-middle sm:w-80 h-0.5 w-96 m-4 bg-cex rounded"></div>
              </div>
                <div className="list-form  flex justify-center align-middle">
                  <input className="w-24 bg-gray-100 bg-opacity-50 rounded border border-gray-300 focus:border-blue-200 focus:ring-2 focus:ring-blue-100 text-base outline-none text-gray-700 py-1 px-4  leading-8 transition-colors duration-200 ease-in-out" type="number" min="1" value={amount} name="input-amount" id="input-amount" onChange={(e) => setAmount(e.target.value)} />
                </div>
                <p id="helper-text-explanation" className="mb-4 text-sm flex justify-center align-middle text-gray-500 dark:text-gray-400">You need to first approve the tokens for issuing new clustors.</p>
                <div className="grid grid-rows-1 grid-flow-col gap-1">
                  
<div className="inline-flex rounded-md shadow-sm  justify-center align-middle">
  <button type="button" className="inline-flex items-center py-2 px-4 text-sm font-medium  rounded-l-lg text-white bg-cex focus:outline-none hover:bg-rex" onClick={onApprove}>
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="w-6 h-6 m-1">
  <path stroke-linecap="round" stroke-linejoin="round" d="M11.35 3.836c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m8.9-4.414c.376.023.75.05 1.124.08 1.131.094 1.976 1.057 1.976 2.192V16.5A2.25 2.25 0 0118 18.75h-2.25m-7.5-10.5H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V18.75m-7.5-10.5h6.375c.621 0 1.125.504 1.125 1.125v9.375m-8.25-3l1.5 1.5 3-3.75" />
</svg>{loading ? "Loading.." : "Approve"}
  </button>
  <button type="button" className="inline-flex items-center py-2 px-4 text-sm font-medium    text-white bg-cex focus:outline-none hover:bg-rex" onClick={onIssue} id="b1">
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="w-6 h-6 m-1">
  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0112 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0112 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z" />
</svg>{loading ? "Loading.." : "Issue"}
  </button>
  <button type="button" className="inline-flex items-center py-2 px-4 text-sm font-medium   text-white bg-cex focus:outline-none hover:bg-rex" onClick={onLock} id="b3">
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="w-6 h-6 m-1">
  <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
</svg>{loading ? "Loading.." : "Lock"}
  </button>
  <button type="button" className="inline-flex items-center py-2 px-4 text-sm font-medium   text-white bg-cex focus:outline-none hover:bg-rex" onClick={onUnlock} id="b4">
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="w-6 h-6 m-1">
  <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 10.5V6.75a4.5 4.5 0 119 0v3.75M3.75 21.75h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H3.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
</svg>{loading ? "Loading.." : "Unlock"}
  </button>
  <button type="button" className="inline-flex items-center py-2 px-4 text-sm font-medium rounded-r-md   text-white bg-cex focus:outline-none hover:bg-rex" onClick={onRedeem} id="b2">
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="w-6 h-6 m-1">
  <path stroke-linecap="round" stroke-linejoin="round" d="M9 14.25l6-6m4.5-3.493V21.75l-3.75-1.5-3.75 1.5-3.75-1.5-3.75 1.5V4.757c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0c1.1.128 1.907 1.077 1.907 2.185zM9.75 9h.008v.008H9.75V9zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm4.125 4.5h.008v.008h-.008V13.5zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
</svg>{loading ? "Loading.." : "Redeem"}
  </button>
  
</div>

                </div>
                <div className="">
            <h3 className="mb-4 flex justify-center align-middle text-2xl font-bold tracking-tight leading-none text-gray-700 md:text-xl lg:text-2xl my-4">Flash Loan</h3>
            <p id="helper-text-explanation" className="mb-4 text-sm flex justify-center align-middle text-gray-500 dark:text-gray-400">Make sure the tokens are pre-approved for the flash loan and include decimal zeroes in the amount.</p>
            <div className="">
            <label for="name" className="leading-7 text-l text-gray-600">Token Address</label>
            <input type="text" id="token-address" className="w-full bg-gray-100 bg-opacity-50 rounded border border-gray-300 focus:border-blue-200 focus:ring-2 focus:ring-blue-100 text-base outline-none text-gray-700 py-1 px-6 leading-8 transition-colors duration-200 ease-in-out"onChange={(e) => setTokenFlash(e.target.value)} />
            <label for="name" className="leading-7 text-l text-gray-600">Contact Address</label>
            <input type="text" id="contract-address"  className="w-full bg-gray-100 bg-opacity-50 rounded border border-gray-300 focus:border-blue-200 focus:ring-2 focus:ring-blue-100 text-base outline-none text-gray-700 py-1 px-6 leading-8 transition-colors duration-200 ease-in-out" onChange={(e) => setFlashAddress(e.target.value)} />
            
            <label for="name" className="mt-1 mb-2 flex justify-center align-middle leading-7 text-l text-gray-600">Amount<br></br></label>
            <div className="flex justify-center align-middle">
            <input type="number" min="1" name="flash-amount" id="flash-amount" className=" w-24 bg-gray-100 bg-opacity-50 rounded border border-gray-300 focus:border-blue-200 focus:ring-2 focus:ring-blue-100 text-base outline-none text-gray-700 py-1 px-4  leading-8 transition-colors duration-200 ease-in-out " onChange={(e) => setFlashAmount(e.target.value)} />
            </div>
            
            <h3 className="my-4 text-lg flex justify-center align-middle font-semibold text-gray-700 md:text-xl lg:text-xl">{"Total Locked Clustors : " + lockedClustors}</h3>
            <span className="mb-4 text-sm flex justify-center align-middle text-gray-500 dark:text-gray-400">The entry-point of the flash loan contract should be named - "execute_operation"</span>
            <div className="flex justify-center align-middle">
              
            <button className="inline-flex text-white bg-cex border-0 py-2 px-6 focus:outline-none hover:bg-rex rounded text-lg" onClick={onFlash}><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="mt-0.5 mr-0.5 w-6 h-6">
  <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
</svg>
{loading ? "Loading.." : "Execute"}</button>
            </div>
            </div>
            </div>

            
            </div>
          </div>
        </div>

        // Alert Message ka css hai dekh lena alert 2 error ka hai alert 3 txn succesful ka hai
/* 
<div id="alert-2" className="flex p-4 mb-4 bg-red-100 rounded-lg dark:bg-red-200" role="alert">
<svg aria-hidden="true" className="flex-shrink-0 w-5 h-5 text-red-700 dark:text-red-800" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>
<span className="sr-only">Info</span>
<div className="ml-3 text-sm font-medium text-red-700 dark:text-red-800">
  A simple info alert with an <a href="#" className="font-semibold underline hover:text-red-800 dark:hover:text-red-900">example link</a>. Give it a click if you like.
</div>
<button type="button" className="ml-auto -mx-1.5 -my-1.5 bg-red-100 text-red-500 rounded-lg focus:ring-2 focus:ring-red-400 p-1.5 hover:bg-red-200 inline-flex h-8 w-8 dark:bg-red-200 dark:text-red-600 dark:hover:bg-red-300" data-dismiss-target="#alert-2" aria-label="Close">
  <span className="sr-only">Close</span>
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
</button>
</div>
<div id="alert-3" className="flex p-4 mb-4 bg-green-100 rounded-lg dark:bg-green-200" role="alert">
<svg aria-hidden="true" className="flex-shrink-0 w-5 h-5 text-green-700 dark:text-green-800" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>
<span className="sr-only">Info</span>
<div className="ml-3 text-sm font-medium text-green-700 dark:text-green-800">
  A simple info alert with an <a href="#" className="font-semibold underline hover:text-green-800 dark:hover:text-green-900">example link</a>. Give it a click if you like.
</div>
<button type="button" className="ml-auto -mx-1.5 -my-1.5 bg-green-100 text-green-500 rounded-lg focus:ring-2 focus:ring-green-400 p-1.5 hover:bg-green-200 inline-flex h-8 w-8 dark:bg-green-200 dark:text-green-600 dark:hover:bg-green-300" data-dismiss-target="#alert-3" aria-label="Close">
  <span className="sr-only">Close</span>
  <svg aria-hidden="true" className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
</button>
</div> */
    );
};

export default Clustor;
