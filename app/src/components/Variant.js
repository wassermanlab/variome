import Card from '@mui/material/Card'
import Typography from '@mui/material/Typography'
import CardContent from '@mui/material/CardContent'
import Button from '@mui/material/Button'

const Variant = () => {
  const copyToClipboard = () => {
    const alleleFrequency = '21-27107251-C-G'; // Replace 
    navigator.clipboard.writeText(alleleFrequency)
      .then(() => {
        
      })
      .catch((error) => {
        console.error('Error copying to clipboard:', error);
      });
  };

  return (
    <Card sx={{ padding: '16px', display: 'flex', flexDirection: 'row', justifyContent: 'space-between' }}>
      <CardContent>
        <Typography variant='h4' sx={{ alignSelf: 'flex-start', marginBottom: '8px' }}>21-27107251-C-G</Typography>
        <Button variant="outlined" onClick={copyToClipboard} sx={{ alignSelf: 'flex-start' }}>
          ⧉ Copy variant ID
        </Button>
      </CardContent>
      <CardContent sx={{ textAlign: 'right' }}>
        <Typography variant='body2' sx={{ letterSpacing: '0.25px' }}>
          Alternate allele
        </Typography>
        <Typography variant='h5' sx={{ my: '16px', color: 'primary.main' }}>
          G
        </Typography>
        <Typography variant='body2' sx={{ letterSpacing: '0.25px' }}>
          Allele frequency
        </Typography>
        <Typography variant='h5' sx={{ my: '16px', color: 'primary.main' }}>
          1.156E-02
        </Typography>
      </CardContent>
    </Card>
  )
}

export default Variant