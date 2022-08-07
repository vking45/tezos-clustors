import axios from "axios";
import {bytes2Char} from "@taquito/utils";

export const fetchStorage = async (contract_address) => {
    const res = await axios.get("https://api.jakartanet.tzkt.io/v1/contracts/"+ contract_address +"/storage");
    return res.data;
}

export const fetchSupply = async (token_address) => {
    const res = await axios.get("https://api.jakartanet.tzkt.io/v1/contracts/"+ token_address +"/storage");
    return res.data.totalSupply;
}

export const fetchClustorName = async (clustor_address) => {
    const res = await axios.get("https://api.jakartanet.tzkt.io/v1/contracts/"+ clustor_address +"/storage");
    return res.data.clustorName;
}

export const fetchClustors = async () => {
    const res = await axios.get("https://api.jakartanet.tzkt.io/v1/contracts/KT1G9kF5QpFw3g2MskqyD9r6kFEgvg7z6FvS/storage");
    return res.data;    
}

export const fetchLocked = async (contract_address) => {
    const res = await axios.get("https://api.jakartanet.tzkt.io/v1/contracts/"+ contract_address +"/storage");
    return res.data.lockedClustors;
}

export const fetchTokenMetaData = async (token_address) => {
    const res = await axios.get("https://api.jakartanet.tzkt.io/v1/contracts/"+ token_address +"/bigmaps/token_metadata/keys/0/");
    let dec = bytes2Char(res.data.value.token_info.decimals);
    let sym = bytes2Char(res.data.value.token_info.symbol);
    return {dec , sym};
}
