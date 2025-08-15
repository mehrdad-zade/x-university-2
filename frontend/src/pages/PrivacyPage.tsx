import { Link } from 'react-router-dom';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white shadow-lg rounded-lg p-8">
          <div className="mb-8">
            <Link 
              to="/register" 
              className="inline-flex items-center text-blue-600 hover:text-blue-500 mb-4"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Registration
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">Privacy Policy</h1>
            <p className="mt-2 text-sm text-gray-600">
              Last updated: August 14, 2025
            </p>
          </div>

          <div className="prose prose-blue max-w-none">
            <h2>1. Information We Collect</h2>
            
            <h3>Personal Information</h3>
            <p>When you create an account, we collect:</p>
            <ul>
              <li>Name and email address</li>
              <li>Account role (student, instructor, administrator)</li>
              <li>Password (stored securely using industry-standard hashing)</li>
            </ul>

            <h3>Usage Information</h3>
            <p>We automatically collect:</p>
            <ul>
              <li>Login and session information</li>
              <li>Course progress and completion data</li>
              <li>System logs for security and performance monitoring</li>
              <li>IP addresses and browser information for security purposes</li>
            </ul>

            <h2>2. How We Use Your Information</h2>
            <p>We use your personal information to:</p>
            <ul>
              <li>Provide and maintain our educational services</li>
              <li>Authenticate your identity and secure your account</li>
              <li>Track your learning progress and provide personalized recommendations</li>
              <li>Communicate with you about your account and our services</li>
              <li>Improve our platform and develop new features</li>
              <li>Ensure platform security and prevent fraud</li>
            </ul>

            <h2>3. Information Sharing</h2>
            <p>
              We do not sell, trade, or rent your personal information to third parties. We may share 
              your information only in the following circumstances:
            </p>
            <ul>
              <li>With instructors for courses you're enrolled in (progress and completion data)</li>
              <li>When required by law or to respond to legal processes</li>
              <li>To protect our rights, privacy, safety, or property</li>
              <li>In connection with a merger, acquisition, or sale of assets (with prior notice)</li>
            </ul>

            <h2>4. Data Security</h2>
            <p>We implement industry-standard security measures to protect your information:</p>
            <ul>
              <li>Passwords are hashed using strong cryptographic algorithms</li>
              <li>Data transmission is encrypted using HTTPS/TLS</li>
              <li>Access to personal data is restricted to authorized personnel only</li>
              <li>Regular security audits and monitoring</li>
              <li>Account lockout mechanisms to prevent brute force attacks</li>
              <li>Session management with secure token rotation</li>
            </ul>

            <h2>5. Data Retention</h2>
            <p>
              We retain your personal information for as long as your account is active or as needed to 
              provide services. We may also retain and use your information to comply with legal obligations, 
              resolve disputes, and enforce our agreements.
            </p>

            <h2>6. Your Rights</h2>
            <p>You have the right to:</p>
            <ul>
              <li>Access and review your personal information</li>
              <li>Correct inaccurate or incomplete information</li>
              <li>Delete your account and associated data</li>
              <li>Export your data in a portable format</li>
              <li>Opt out of non-essential communications</li>
            </ul>

            <h2>7. Cookies and Tracking</h2>
            <p>
              We use essential cookies and session tokens to provide our services. These include:
            </p>
            <ul>
              <li>Authentication tokens to keep you logged in</li>
              <li>Session cookies for platform functionality</li>
              <li>Local storage for user preferences</li>
            </ul>
            <p>
              We do not use third-party tracking cookies or advertising cookies.
            </p>

            <h2>8. Children's Privacy</h2>
            <p>
              Our service is not directed to children under 13 years of age. We do not knowingly collect 
              personal information from children under 13. If you become aware that a child has provided 
              us with personal information, please contact us.
            </p>

            <h2>9. International Data Transfers</h2>
            <p>
              Your information may be transferred to and maintained on computers located outside of your 
              state, province, country, or other governmental jurisdiction where data protection laws may 
              differ. We ensure appropriate safeguards are in place for such transfers.
            </p>

            <h2>10. Changes to This Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify you of any changes by 
              posting the new Privacy Policy on this page and updating the "Last updated" date.
            </p>

            <h2>11. Contact Us</h2>
            <p>
              If you have questions about this Privacy Policy or our data practices, please contact us at:
            </p>
            <ul>
              <li>Email: privacy@x-university.com</li>
              <li>Data Protection Officer: dpo@x-university.com</li>
            </ul>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <Link 
                to="/terms" 
                className="text-blue-600 hover:text-blue-500"
              >
                ← Terms of Service
              </Link>
              <Link 
                to="/register" 
                className="text-blue-600 hover:text-blue-500"
              >
                Back to Registration →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
