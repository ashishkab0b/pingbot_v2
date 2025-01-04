import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Typography,
    Box,
} from '@mui/material';

function DonationDialog({ open, onClose }) {
    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle>Thank you for using Pingbot!</DialogTitle>
            <DialogContent dividers>
                <Typography paragraph>
                    As a graduate student, I’ve poured countless hours into designing,
                    coding, and refining this tool to ensure it meets the needs of the
                    research community. Your support helps recognize the time, investment,
                    and expertise that went into creating and maintaining this resource.
                    Donations allow me to:
                </Typography>
                <Typography paragraph>
                    <ul>
                        <li>Continue improving the tool with new features</li>
                        <li>Provide support to users</li>
                        <li>
                            Dedicate more time to ensuring the application remains free
                            and accessible for all
                        </li>
                    </ul>
                </Typography>
                <Typography paragraph>
                    If this tool has been helpful to you, please consider donating. <u>Any amount is greatly appreciated</u>, but <strong>a suggested contribution is 1 dollar per participant per study</strong>. 
                    {/* <strong>Suggested contributions per study are:</strong>
                    <ul>
                        <li>$20 per study for individuals</li>
                        <li>$50-$200 per study for groups with research funding</li>
                    </ul> */}
                </Typography>
                <Typography paragraph>
                    However, if you are unable to contribute, please don’t worry! Pingbot is and will always be completely free to use.
  
                    Thank you for your support!
                </Typography>

                <Box
                    mt={2}
                    display="flex"
                    justifyContent="center"
                >
                    <stripe-buy-button
                        buy-button-id="buy_btn_1QdCKmGAf1R453AQH8vl4nwX"
                        publishable-key="pk_live_51QdBvMGAf1R453AQL9xskuy6XyHKbYORN3I4AV1KhsDuvGnNRR6QV3CsIiZ2rbnRBg65F34PEii9esiviIOSEt2n00Xi1lwmqe"
                    />
                </Box>
            </DialogContent>
            <DialogActions>
                {/* "Skip" button just closes the dialog */}
                <Button onClick={onClose} variant="contained" color="secondary">
                    Skip
                </Button>
            </DialogActions>
        </Dialog>
    );
}

export default DonationDialog;