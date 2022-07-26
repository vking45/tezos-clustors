import logo2 from "../assets/logo2.png";
 
const Footer = () => {
    return (
        <footer className="text-gray-600 body-font-helvetica">
                <div className="container px-5 py-8 mx-auto flex items-center sm:flex-row flex-col">
            <a className="flex title-font font-medium items-center md:justify-start justify-center text-gray-900" href="/">
    <img src={logo2} className="w-20 h-18" alt="logo"/>
      <span className="text-3xl font-bold text-rex cursor-pointer -ml-3">LUSTORS</span>
    </a>
    <p className="text-md text-gray-500 sm:ml-4 sm:pl-4 sm:border-l-2 sm:border-gray-200 sm:py-2 sm:mt-0 mt-4">Potential Future Developments - Switch Clustors & Dynamic Clustors.
    </p>
    
  </div>
</footer>
    );
}

export default Footer;
