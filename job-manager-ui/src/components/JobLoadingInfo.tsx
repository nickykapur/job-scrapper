import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandIcon,
  Storage as DatabaseIcon,
  CloudOff as NoScrapingIcon,
  Computer as LocalIcon,
  CloudSync as SyncIcon,
  Schedule as AutoRefreshIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

interface JobLoadingInfoProps {
  jobCount: number;
}

export const JobLoadingInfo: React.FC<JobLoadingInfoProps> = ({ jobCount }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card sx={{ mb: 3, border: '1px solid', borderColor: 'info.main', borderRadius: 2 }}>
      <Accordion 
        expanded={expanded} 
        onChange={() => setExpanded(!expanded)}
        elevation={0}
        sx={{ backgroundColor: 'transparent' }}
      >
        <AccordionSummary expandIcon={<ExpandIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
            <InfoIcon color="info" />
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              How Jobs Are Loaded
            </Typography>
            <Chip 
              icon={<DatabaseIcon />} 
              label={`${jobCount} Jobs Available`} 
              color="primary" 
              size="small" 
            />
          </Box>
        </AccordionSummary>
        
        <AccordionDetails>
          <Box sx={{ mb: 3 }}>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
              Your LinkedIn Job Manager uses a hybrid approach for loading jobs:
            </Typography>
            
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <DatabaseIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary="Static Database Loading"
                  secondary="Jobs are loaded from your existing jobs_database.json file containing 35+ pre-scraped jobs"
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon>
                  <NoScrapingIcon color="warning" />
                </ListItemIcon>
                <ListItemText
                  primary="No Live Scraping on Railway"
                  secondary="Web scraping is disabled on Railway deployment due to browser/Chrome limitations"
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon>
                  <AutoRefreshIcon color="info" />
                </ListItemIcon>
                <ListItemText
                  primary="Auto-Refresh Every 5 Minutes"
                  secondary="The app automatically refreshes job data from the database to check for any updates"
                />
              </ListItem>
            </List>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Box>
            <Typography variant="h6" gutterBottom>
              🔄 How to Add New Jobs
            </Typography>
            
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <LocalIcon color="success" />
                </ListItemIcon>
                <ListItemText
                  primary="Run Scraper Locally"
                  secondary="Use 'python main.py search [keywords]' on your local machine with Chrome/Firefox"
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon>
                  <SyncIcon color="info" />
                </ListItemIcon>
                <ListItemText
                  primary="Sync Database File"
                  secondary="Upload your updated jobs_database.json to Railway or use git to sync changes"
                />
              </ListItem>
            </List>
            
            <Box sx={{ mt: 2, p: 2, backgroundColor: 'background.paper', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="body2" color="text.secondary">
                <strong>Pro Tip:</strong> Your app is perfect for managing existing job applications! 
                Use the search, filter, and apply tracking features while running scraping locally when needed.
              </Typography>
            </Box>
          </Box>
        </AccordionDetails>
      </Accordion>
    </Card>
  );
};