import { useEffect, useState } from "react";
import {connectWallet, getAccount} from "../utils/wallet";
import { Link } from 'react-router-dom';
 
const Navbar = () => {
    
    const [account, setAccount] = useState("");
    
    useEffect(() => {
        (async () => {
            const account = await getAccount();
            setAccount(account);        
        })();
    }, [])

    const onConnectWallet = async () => {
        await connectWallet();
        const account = await getAccount();
        setAccount(account);
    }
    
    return (
        <header className="text-gray-600 body-font">
  <div className="container mx-auto flex flex-wrap p-5 flex-col md:flex-row items-center">
    <a className="flex title-font font-medium items-center text-gray-900 mb-4 md:mb-0">
    <img src="images/logo2.png" className="w-20 h-18"/>
      <span className="text-3xl font-bold text-rex -ml-3 cursor-pointer">LUSTORS</span>
    </a>
    <nav className="md:ml-auto flex flex-wrap items-center text-base justify-center">
      <Link to="/clustor"  className="mr-6 text-xl hover:text-gray-900 cursor-pointer mb-3 sm:mb-3">Browse Clustors & Flash Loan</Link>
      <Link to="/create" className="mr-6 text-xl hover:text-gray-900 cursor-pointer mb-3 sm:mb-3">Create Clustor</Link>
    </nav>
    <button className="inline-flex text-white bg-cex border-0 py-2 px-6 focus:outline-none hover:bg-rex rounded text-lg hover:shadow-lg font-medium transition transform hover:-translate-y-0.5"onClick={onConnectWallet}>
      {account ? account : "Connect Wallet"}
    </button>
  </div>
</header>
        
    );
}

export default Navbar;
