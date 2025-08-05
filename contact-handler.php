<?php
// Contact Form Handler for Country's News
// Compatible with Hostinger Shared Hosting

// Enable error reporting for debugging (disable in production)
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Set content type
header('Content-Type: text/html; charset=UTF-8');

// Security headers
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('X-XSS-Protection: 1; mode=block');

// Check if form was submitted via POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    die('Method not allowed');
}

// Configuration
$admin_email = 'news@countrysnews.com'; // Change this to your actual email
$site_name = "Country's News";
$success_message = "Thank you for your message. We'll get back to you soon!";

// Function to sanitize input
function sanitize_input($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data, ENT_QUOTES, 'UTF-8');
    return $data;
}

// Function to validate email
function validate_email($email) {
    return filter_var($email, FILTER_VALIDATE_EMAIL);
}

// Function to log submissions (optional)
function log_submission($data) {
    $log_file = 'contact_log.txt';
    $log_entry = date('Y-m-d H:i:s') . " - " . json_encode($data) . "\n";
    file_put_contents($log_file, $log_entry, FILE_APPEND | LOCK_EX);
}

// Get form type
$form_type = isset($_POST['form_type']) ? sanitize_input($_POST['form_type']) : 'contact';

try {
    if ($form_type === 'newsletter') {
        // Newsletter Subscription
        $email = isset($_POST['email']) ? sanitize_input($_POST['email']) : '';
        
        if (empty($email)) {
            http_response_code(400);
            die('Email is required');
        }
        
        if (!validate_email($email)) {
            http_response_code(400);
            die('Invalid email address');
        }
        
        // Store newsletter subscription (you can modify this to use a database)
        $newsletter_file = 'newsletter_subscribers.txt';
        $subscriber_data = date('Y-m-d H:i:s') . " - " . $email . "\n";
        file_put_contents($newsletter_file, $subscriber_data, FILE_APPEND | LOCK_EX);
        
        // Send confirmation email
        $subject = "Newsletter Subscription Confirmation - $site_name";
        $message = "
        <html>
        <head>
            <title>Newsletter Subscription Confirmation</title>
        </head>
        <body>
            <h2>Welcome to $site_name Newsletter!</h2>
            <p>Thank you for subscribing to our newsletter. You'll receive the latest news and updates directly in your inbox.</p>
            <p>If you didn't subscribe to this newsletter, please ignore this email.</p>
            <hr>
            <p><small>This email was sent from $site_name</small></p>
        </body>
        </html>
        ";
        
        $headers = "MIME-Version: 1.0" . "\r\n";
        $headers .= "Content-type:text/html;charset=UTF-8" . "\r\n";
        $headers .= "From: $admin_email" . "\r\n";
        
        mail($email, $subject, $message, $headers);
        
        // Send notification to admin
        $admin_subject = "New Newsletter Subscription - $site_name";
        $admin_message = "New newsletter subscription: $email";
        mail($admin_email, $admin_subject, $admin_message);
        
        echo "Newsletter subscription successful!";
        
    } else {
        // Contact Form
        $name = isset($_POST['name']) ? sanitize_input($_POST['name']) : '';
        $email = isset($_POST['email']) ? sanitize_input($_POST['email']) : '';
        $subject = isset($_POST['subject']) ? sanitize_input($_POST['subject']) : '';
        $message = isset($_POST['message']) ? sanitize_input($_POST['message']) : '';
        $newsletter_subscribe = isset($_POST['newsletter_subscribe']) ? true : false;
        
        // Validation
        $errors = [];
        
        if (empty($name)) {
            $errors[] = 'Name is required';
        }
        
        if (empty($email)) {
            $errors[] = 'Email is required';
        } elseif (!validate_email($email)) {
            $errors[] = 'Invalid email address';
        }
        
        if (empty($subject)) {
            $errors[] = 'Subject is required';
        }
        
        if (empty($message)) {
            $errors[] = 'Message is required';
        }
        
        if (!empty($errors)) {
            http_response_code(400);
            die(implode(', ', $errors));
        }
        
        // Subject mapping
        $subject_map = [
            'news_tip' => 'News Tip',
            'story_idea' => 'Story Idea',
            'press_release' => 'Press Release',
            'general_inquiry' => 'General Inquiry',
            'technical_issue' => 'Technical Issue',
            'advertising' => 'Advertising Inquiry'
        ];
        
        $subject_text = isset($subject_map[$subject]) ? $subject_map[$subject] : 'General Inquiry';
        
        // Prepare email to admin
        $admin_subject = "New Contact Form Submission: $subject_text - $site_name";
        $admin_message = "
        <html>
        <head>
            <title>New Contact Form Submission</title>
        </head>
        <body>
            <h2>New Contact Form Submission</h2>
            <p><strong>Name:</strong> $name</p>
            <p><strong>Email:</strong> $email</p>
            <p><strong>Subject:</strong> $subject_text</p>
            <p><strong>Newsletter Subscribe:</strong> " . ($newsletter_subscribe ? 'Yes' : 'No') . "</p>
            <p><strong>Message:</strong></p>
            <div style='background-color: #f5f5f5; padding: 15px; border-radius: 5px;'>
                " . nl2br($message) . "
            </div>
            <hr>
            <p><small>Submitted on: " . date('Y-m-d H:i:s') . "</small></p>
        </body>
        </html>
        ";
        
        $headers = "MIME-Version: 1.0" . "\r\n";
        $headers .= "Content-type:text/html;charset=UTF-8" . "\r\n";
        $headers .= "From: $email" . "\r\n";
        $headers .= "Reply-To: $email" . "\r\n";
        
        // Send email to admin
        if (mail($admin_email, $admin_subject, $admin_message, $headers)) {
            // Send confirmation email to user
            $user_subject = "Message Received - $site_name";
            $user_message = "
            <html>
            <head>
                <title>Message Received</title>
            </head>
            <body>
                <h2>Thank you for contacting $site_name!</h2>
                <p>Dear $name,</p>
                <p>We have received your message regarding: <strong>$subject_text</strong></p>
                <p>Our team will review your message and get back to you within 24 hours.</p>
                <p>For urgent news tips, we typically respond within 2 hours.</p>
                <hr>
                <p>Best regards,<br>The $site_name Team</p>
            </body>
            </html>
            ";
            
            $user_headers = "MIME-Version: 1.0" . "\r\n";
            $user_headers .= "Content-type:text/html;charset=UTF-8" . "\r\n";
            $user_headers .= "From: $admin_email" . "\r\n";
            
            mail($email, $user_subject, $user_message, $user_headers);
            
            // Log the submission
            log_submission([
                'type' => 'contact',
                'name' => $name,
                'email' => $email,
                'subject' => $subject_text,
                'message' => substr($message, 0, 100) . '...',
                'newsletter' => $newsletter_subscribe
            ]);
            
            // If user wants newsletter subscription
            if ($newsletter_subscribe) {
                $newsletter_file = 'newsletter_subscribers.txt';
                $subscriber_data = date('Y-m-d H:i:s') . " - " . $email . " (via contact form)\n";
                file_put_contents($newsletter_file, $subscriber_data, FILE_APPEND | LOCK_EX);
            }
            
            echo $success_message;
            
        } else {
            http_response_code(500);
            die('Failed to send email. Please try again later.');
        }
    }
    
} catch (Exception $e) {
    http_response_code(500);
    die('An error occurred. Please try again later.');
}
?>
