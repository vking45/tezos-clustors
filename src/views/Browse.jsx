import { lazy } from "react";

import { useState, useEffect } from "react";

import {fetchClustors, fetchClustorName} from "../utils/tzkt";

const List = lazy(() => import("../components/List")); 

let ListTitles = [];

const Browse = () => {
    
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
  return(
   <section className="m-auto p-auto h-max">
    <List listTitles={ListTitles}/>   
   </section>  
  );
};
 
export default Browse;
