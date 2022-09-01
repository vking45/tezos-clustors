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
           <h1 className="mb-4 text-3xl flex justify-center align-middle font-extrabold tracking-tight leading-none text-gray-900 md:text-2xl lg:text-4xl dark:text-gray">{name}</h1>
          {clustorStatus ?
            <div className="wrapper">
            <h3 className="mb-4 text-2xl flex justify-center align-middle font-bold tracking-tight leading-none text-gray-800 md:text-xl lg:text-4xl">{"Clustor Supply : " + totalSupply}</h3>
            <span className="mb-2 text-lg flex justify-center align-middle font-normal text-gray-600 lg:text-xl sm:px-16 xl:px-48 dark:text-gray-600">{"Clustor Address : " + ctokenAddress}</span>
            <span className="mb-6 text-lg flex justify-center align-middle font-normal text-gray-600 lg:text-xl sm:px-16 xl:px-48 dark:text-gray-600">Add this token address to your respective wallets</span>
          </div>
          :
            <button className="py-2.5 px-5 mr-2 text-sm font-medium text-gray-900 bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 inline-flex items-center" onClick={onInit}>{loading ? "Loading...":"Initialize"}
            </button>
          }
        
          <div className="flex flex-row justify-start">

            <div className="w-1/2">
              <h3 className="mb-4 text-2xl font-bold tracking-tight leading-none text-gray-800 md:text-xl lg:text-4xl">Token List</h3>
              <TokensList addresses={ListAddresses} />
                <div className="list-form">
                  <input className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" type="number" min="1" value={amount} name="input-amount" id="input-amount" onChange={(e) => setAmount(e.target.value)} />
                  <p id="helper-text-explanation" className="mt-2 text-sm text-gray-500 dark:text-gray-400">**You need to first approve the tokens for issuing new clustors.</p>
                </div>
            </div>
          </div>
        </div>
    );
};

export default Clustor;
