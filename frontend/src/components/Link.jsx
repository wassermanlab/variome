import { Link as RouterLink } from 'react-router-dom';
import { Link as MuiLink } from '@mui/material';

export default function Link(props) {
  return <MuiLink component={RouterLink} {...props} />;
}