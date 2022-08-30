import { useEffect, useState } from "react";
import {connectWallet, getAccount} from "../utils/wallet";
import logo2 from "../assets/logo2.png";
 
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
    <a className="flex title-font font-medium items-center text-gray-900 mb-4 md:mb-0" href="/">
    <img src={logo2} className="w-20 h-18" alt="logo"/>
      <span className="text-3xl font-bold text-rex -ml-3 cursor-pointer">LUSTORS</span>
    </a>
    <nav className="md:ml-auto flex flex-wrap items-center text-base justify-center">
      <a href="{'/clustors/browse/${clustor.address}/'}"  className="mr-6 text-xl hover:text-gray-900 cursor-pointer mb-3 sm:mb-3">Browse</a>
      <a href="/clustors/create" className="mr-6 text-xl hover:text-gray-900 cursor-pointer mb-3 sm:mb-3">Create Clustor</a>
    </nav>
    <button className="inline-flex text-white bg-cex border-0 mb-2 py-2 px-6 focus:outline-none hover:bg-rex rounded text-lg hover:shadow-lg font-medium transition transform hover:-translate-y-0.5"onClick={onConnectWallet}>
      {account ? account : "Connect Wallet"}
    </button>
  </div>
</header>
        
    );
}

export default Navbar;
