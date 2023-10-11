import useMediaQuery from '@mui/material/useMediaQuery'

import VerticalLayout from './verticalLayout'
import VerticalNavItems from 'src/navigation/vertical'
import VerticalAppBarContent from './components/vertical/AppBarContent'

import { useSettings } from 'src/@core/hooks/useSettings'

const UserLayout = ({ children }) => {
  const { settings, saveSettings } = useSettings()
  const hidden = useMediaQuery(theme => theme.breakpoints.down('lg'))

  return (
    <VerticalLayout
      hidden={hidden}
      settings={settings}
      saveSettings={saveSettings}
      verticalNavItems={VerticalNavItems()} 
      verticalAppBarContent={(
        props 
      ) => (
        <VerticalAppBarContent
          hidden={hidden}
          settings={settings}
          saveSettings={saveSettings}
          toggleNavVisibility={props.toggleNavVisibility}
        />
      )}
    >
      {children}
    </VerticalLayout>
  )
}

export default UserLayout
