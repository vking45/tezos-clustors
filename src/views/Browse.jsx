import {fetchClustors, fetchClustorName} from "../utils/tzkt";
import { useState, useEffect } from "react";
import { lazy } from "react";
import React from "react";
const List = lazy(() => import("../components/List"));
const Broswe = () => {
  let ListTitles = [];

const [loading, setLoading] = useState(true);

    useEffect(() => {
        (async () => {
            const clustorList = await fetchClustors();
            for (const i in clustorList){
                let clustorName = await fetchClustorName(clustorList[i]);
                ListTitles.push({address: clustorList[i], cname: clustorName});            
            }
            setLoading(false);                  
        })(); 
        
        return () => {
            setLoading(true);
            ListTitles = [];
        }
       
    }, []); 

  return ( 
    <List listTitles={ListTitles}/>
   );
}
 
export default Broswe;