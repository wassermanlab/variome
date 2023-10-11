import Grid from '@mui/material/Grid'
import Variant from '../components/Variant'
import Annotations from '../components/Annotations'
import References from '../components/References'
import Overview from '../components/Overview'

const Dashboard = () => {
  return (
      <Grid container spacing={6}>
        <Grid item xs={12} md={8}>
          <Grid container direction="column" spacing={2}>
            <Grid item xs={12}>
                <Variant />
            </Grid>
            <Grid item xs={12}>
              <Overview />
            </Grid>
          </Grid>
        </Grid>
        <Grid item xs={12} md={4}>
          <References />
        </Grid>
        <Grid item xs={12}>
          <Annotations />
        </Grid>
      </Grid>
  )
}

export default Dashboard
