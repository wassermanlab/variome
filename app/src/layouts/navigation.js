import HomeOutline from 'mdi-material-ui/HomeOutline'
import Information from 'mdi-material-ui/Information'
import AccountGroup from 'mdi-material-ui/AccountGroup'
import Database from 'mdi-material-ui/Database'
import HelpCircle from 'mdi-material-ui/HelpCircle'
import NoteText from 'mdi-material-ui/NoteText'
import BookOpenPageVariant from 'mdi-material-ui/BookOpenPageVariant'
import Briefcase from 'mdi-material-ui/Briefcase'
import Email from 'mdi-material-ui/Email'

const navigation = () => {
  return [
    {
      title: 'Home',
      icon: HomeOutline,
      path: '/'
    },
    {
      title: 'About',
      icon: Information,
      path: '/about'
    },
    {
      title: 'Team',
      icon: AccountGroup,
      path: '/team'
    },
    {
      title: 'IBVL',
      icon: Database,
      path: '/ibvl'
    },
    {
      title: 'FAQ',
      icon: HelpCircle,
      path: '/faq'
    },
    {
      title: 'Terms of Use',
      icon: NoteText,
      path: '/termsofuse'
    },
    {
      title: 'Resources',
      icon: BookOpenPageVariant,
      path: '/resources'
    },
    {
      title: 'Careers',
      icon: Briefcase,
      path: '/careers'
    },
    {
      title: 'Contact Us',
      icon: Email,
      path: '/contactus'
    }
  ]
}

export default navigation