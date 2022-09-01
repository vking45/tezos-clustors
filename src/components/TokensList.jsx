const TokensList = ({ addresses }) => {
    return (    
        <div className="list">
            {
                addresses.map((address) => (
                    <div className="flex flex-row justify-between align-middle text-white bg-blue-100 rounded-sm mt-2 w-1/2 overflow-hidden" key={address.address}>
                        <h4 className="font-light font-sm text-gray-700 m-2">{ address.sym + " - " + address.address }</h4>
                        <p className="font-light font-sm text-gray-700 m-2">{ address.value }</p>
                    </div>
                ))
            } 
        </div>
    );
};

export default TokensList;
