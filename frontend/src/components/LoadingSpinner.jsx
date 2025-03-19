import {Oval} from 'react-loader-spinner';

export default function LoadingSpinner(){
  return <span style={{display:"flex", justifyContent:"center"}} aria-label='loading indicator'>
    <Oval color="black" secondaryColor="grey" style={{background:"blue"}}/>
    </span>
}