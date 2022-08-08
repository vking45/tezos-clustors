import "./styles/tokens_list.css";

const TokensList = ({ addresses }) => {
    return (    
        <div className="list">
            {
                addresses.map((address) => (
                    <div className="token-element" key={address.address}>
                        <h4 className="address">{ address.sym + " - " + address.address }</h4>
                        <p className="address-value">{ address.value }</p>
                    </div>
                ))
            } 
        </div>
    );
};

export default TokensList;
