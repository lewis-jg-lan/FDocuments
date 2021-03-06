//
//  UnitViewController.m
//  DUT
//
//  Created by Ryan on 11/3/15.
//  Copyright © 2015 ___Intelligent Automation___. All rights reserved.
//

#import "UnitViewController.h"
#include "AppDelegate.h"

#include "RegexKitLite.h"

@interface UnitViewController ()

@end

#define REQUEST_ADDRESS         @"REQUEST_ADDRESS"
#define SUBSCRIBER_ADDRESS      @"SUBSCRIBER_ADDRESS"

@implementation UnitViewController

-(id)initialwithID:(int)ID
{
    //self = [super init];
    self = [super initWithNibName:@"UnitViewController" bundle:[NSBundle bundleForClass:[self class]]];
    if (self) {
        mID = ID;
        pDUT = new CDUTController(mID);
        pDUT->SetDelegate(self);
    }
    
    return self;
}


-(int)InitialPort:(NSDictionary *)diConfig
{
    pDUT->Close();
    pDUT->Initial([[diConfig valueForKey:kRequest] UTF8String], [[diConfig valueForKey:kSubscribe] UTF8String]);
    return 0;
}
- (void)viewDidLoad {
    [super viewDidLoad];
    // Do view setup here.
    [txtBuffer setUsesFindBar:YES];
}

-(void)awakeFromNib
{
//    NSLog(@"Initial Uint in here!,ID: %d @%p",mID,self);
}
-(void)dealloc
{
    NSLog(@"dealloc object");
    if (pDUT)
    {
        delete pDUT;
        pDUT = nullptr;
    }
    [super dealloc];
}
-(IBAction)btSend:(id)sender
{
    int ret = pDUT->WriteString([[[comboxCmd stringValue] stringByAppendingString:@"\r\n"] UTF8String]);
    if (ret<0)
    {
        //NSRunAlertPanel(@"Write DUT", @"Write DUT%d failed,please check connection,or make sure TestEngine is running", @"OK", nil, nil,mID);
        NSAlert * alert = [[NSAlert alloc] init];
        alert.messageText = [NSString stringWithFormat:@"Write DUT%d failed",mID];
        alert.informativeText = @"Replier not response,Please make sure TestEngine is running";
        [alert runModal];
        [alert release];
    }
}


-(void)OnLog:(NSString *)str
{
    if (!str) return;
    NSMutableString * pstr = [[txtBuffer textStorage] mutableString];
    [pstr appendFormat:@"%@",str];
    NSRange range = NSMakeRange([pstr length]-1,0);
    [txtBuffer scrollRangeToVisible:range];
}

#define TIME_STAMP_MATCH        @"[0-9A-Fa-f]+@R\\d"
#define TIME_STAMP_MATCH_CAP    @"([0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])([0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])@R\\d"
-(NSString *)ReplaceTimeStamp:(NSString *)str
{
    return [str stringByReplacingOccurrencesOfRegex:TIME_STAMP_MATCH options:RKLMultiline inRange:NSMakeRange(0, [str length]-1) error:nil enumerationOptions:RKLRegexEnumerationNoOptions usingBlock:^NSString *(NSInteger captureCount, NSString *const *capturedStrings, const NSRange *capturedRanges, volatile BOOL *const stop) {
        NSString * cap = [NSString stringWithString:(NSString *)*capturedStrings];
        NSString * strSecond = [cap stringByMatching:TIME_STAMP_MATCH_CAP capture:1];
        NSString * strMS = [cap stringByMatching:TIME_STAMP_MATCH_CAP capture:2];
        if ((!str)||(!strMS)) {
            return @"";
        }
        
        long seconds = strtol([[@"0x" stringByAppendingString:strSecond] UTF8String], NULL, 16);
        long ms = strtol([[@"0x" stringByAppendingString:strMS] UTF8String], NULL, 16);
        NSTimeInterval time = seconds+(double)ms/1000.0;
        
        NSDate * date = [NSDate dateWithTimeIntervalSince1970:time];
        
        NSDateFormatter *dateFormatter = [[NSDateFormatter alloc] init];
        [dateFormatter setDateFormat:@"yyyy/MM/dd HH:mm:ss.SSS : "];
        
        NSString * rep = [dateFormatter stringFromDate:date];

        [dateFormatter release];
        return rep;
        
    }];
}

-(void)OnData:(void *)bytes length:(long)len
{
    if (!len) return;
    NSString * str = [[NSString alloc] initWithBytes:bytes length:len encoding:NSUTF8StringEncoding];
    str = [self ReplaceTimeStamp:str];
    [self performSelectorOnMainThread:@selector(OnLog:)  withObject:str waitUntilDone:NO];
}


@end
