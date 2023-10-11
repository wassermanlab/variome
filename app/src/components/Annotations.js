import Card from '@mui/material/Card'
import Table from '@mui/material/Table'
import TableRow from '@mui/material/TableRow'
import TableHead from '@mui/material/TableHead'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import Typography from '@mui/material/Typography'
import TableContainer from '@mui/material/TableContainer'

const rows = [
  {
    gene: 'ATP5J',
    transcript: 'ENST0000045671.2',
    HGVSc: 'ENST0000283791.3:c.157G>C',
    HGVSp: 'ENSP0000038192.2:p.Gly6Arg',
    OtherAnnotations: 'None',
    Polyphen: 0.769
  },
  {
    gene: 'ATP5J',
    transcript: 'ENST0000045671.2',
    HGVSc: 'ENST0000283791.3:c.157G>C',
    HGVSp: 'ENSP0000038192.2:p.Gly6Arg',
    OtherAnnotations: 'None',
    Polyphen: 0.769
  },  
  {
    gene: 'ATP5J',
    transcript: 'ENST0000045671.2',
    HGVSc: 'ENST0000283791.3:c.157G>C',
    HGVSp: 'ENSP0000038192.2:p.Gly6Arg',
    OtherAnnotations: 'None',
    Polyphen: 0.769
  }
]

const Annotations = () => {
  return (
    <Card>
      <TableContainer>
      <Typography variant='h4'>Annotations</Typography>
        <Table sx={{ minWidth: 800 }} aria-label='table in dashboard'>
          <TableHead>
            <TableRow>
              <TableCell>Gene</TableCell>
              <TableCell>Transcript</TableCell>
              <TableCell>HGVSc</TableCell>
              <TableCell>HGVSp</TableCell>
              <TableCell>Other Annotations</TableCell>
              <TableCell>Polyphen</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map(row => (
              <TableRow hover key={row.name} sx={{ '&:last-of-type td, &:last-of-type th': { border: 0 } }}>
                <TableCell>{row.gene}</TableCell>
                <TableCell>{row.transcript}</TableCell>
                <TableCell>{row.HGVSc}</TableCell>
                <TableCell>{row.HGVSp}</TableCell>
                <TableCell>{row.OtherAnnotations}</TableCell>
                <TableCell>{row.Polyphen}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Card>
  )
}

export default Annotations
