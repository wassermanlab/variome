import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#4d6397',
    },
    secondary: {
      main: '#ebecec',
    },
    background: {
      default: '#f3f3f3'
    },
    highlight: {
      main: '#b3eca4',
      contrastText: '#fff'
    },
  }
});

export default theme;