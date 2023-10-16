import Grid from '@mui/material/Grid'
import Typography from '@mui/material/Typography';


const Home = () => {
    return (
        <Grid container direction="row" justify="center" alignItems="center" alignContent="flex-end" spacing={3}>
            <Grid container direction="column" spacing={2}>
                <Grid item xs={12}>
                    <Typography variant="h1" gutterBottom>
                        Welcome to the IBVL Database
                    </Typography>
                </Grid>
            </Grid>
            <Grid container direction="column" spacing={2}>
                <Grid item xs={12}>
                    <Typography variant="h4" gutterBottom>
                        Search Bar
                    </Typography>
                </Grid>
            </Grid>
            <Grid container direction="column" spacing={2}>
                <Grid item xs={12}>
                    <Typography variant="h4" gutterBottom>
                        Project Overview
                    </Typography>
                </Grid>
            </Grid>
            <Grid container direction="column" spacing={2}>
                <Grid item xs={12}>
                    <Typography variant="h4" gutterBottom>
                        Collaborators
                    </Typography>
                </Grid>
            </Grid>
        </Grid>
  )
}

export default Home