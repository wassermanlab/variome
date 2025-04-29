
import {
  Article,
  Email,
  HelpCenter,
  Home as HomeIcon,
  Info,
  Rule,
  Menu as MenuIcon,
  Description,
  ChevronLeft,
  ChevronRight,
  Star,
  Login,
  Person
} from "@mui/icons-material";

/* How to add content:
  * 1. Create a new .md file in the content directory and add your content in markdown format ( https://commonmark.org/help/ )
  * 1. Add a new entry to the IconMap below with the name of that markdown file and the icon you want to use
  * 3. The icon should also be added to the import statement above, so that it's available for use
  * 
  * See list of available icons at https://mui.com/material-ui/material-icons/
  * You can reorder these entries to change sorting of the menu navigation links
  */
const IconMap = {
//  Home: HomeIcon,
  "About He Kākano": Info,
  "Conditions of Use of the Variome Dataset": Rule,
  Contact: Email,
}

IconMap.default = Description;

export default IconMap;