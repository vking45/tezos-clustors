const TokensList = ({ addresses }) => {
    return (    
        <div className="list">
            {
                addresses.map((address) => (
                    <div className="flex justify-center align-middle text-white rounded-sm mt-4" key={address.address}>
                        <input type="text" id="disabled-input" aria-label="disabled input" className="w-10/12 bg-gray-100 bg-opacity-50 rounded border border-gray-300 focus:border-blue-200 focus:ring-2 focus:ring-blue-100 text-base outline-none text-gray-700 py-1 px-6 leading-8 transition-colors duration-200 ease-in-out" value={ address.sym + " - " + address.address + " : " + address.value }></input>
                    </div>
                ))
            } 
        </div>
    );
};

export default TokensList;
